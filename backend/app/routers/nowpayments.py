from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from typing import Optional

import requests
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.booking import Booking
from app.models.nowpayments_ipn_event import NowPaymentsIpnEvent
from app.models.nowpayments_payment import NowPaymentsPayment
from app.models.payment import Payment as PaymentModel
from app.models.user_entitlement import UserEntitlement
from app.models.product_purchase import ProductPurchase
from app.schemas.nowpayments import CreatePaymentRequest, CreatePaymentResponse, PaymentStatusMinimal
from app.utils.security import verify_nowpayments_signature


logger = logging.getLogger("nowpayments")

router = APIRouter(prefix="/payments", tags=["payments"])

PAID_ACCESS_ENTITLEMENT = "paid_access"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def parse_booking_id(order_id: Optional[str]) -> Optional[int]:
    if not order_id:
        return None
    if not order_id.startswith("booking-"):
        return None
    try:
        return int(order_id.split("booking-")[1])
    except (ValueError, IndexError):
        return None


def parse_product_purchase_id(order_id: Optional[str]) -> Optional[int]:
    if not order_id:
        return None
    if not order_id.startswith("product-"):
        return None
    try:
        return int(order_id.split("product-")[1])
    except (ValueError, IndexError):
        return None


def get_booking_by_payment(db: Session, payment_id: int, order_id: Optional[str]) -> Optional[Booking]:
    booking_id = parse_booking_id(order_id)
    if booking_id:
        return db.query(Booking).filter(Booking.id == booking_id).first()
    return db.query(Booking).filter(Booking.payment_id == str(payment_id)).first()


def nowpayments_request(method: str, path: str, **kwargs):
    api_key = os.getenv("NOWPAYMENTS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="NOWPAYMENTS_API_KEY is not configured")

    base_url = os.getenv("NOWPAYMENTS_API_BASE", "https://api.nowpayments.io/v1").rstrip("/")
    timeout = float(os.getenv("NOWPAYMENTS_TIMEOUT", "15"))
    url = f"{base_url}{path}"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="NOWPayments API is unavailable") from exc

    if response.status_code >= 400:
        detail = "NOWPayments API error"
        try:
            error_data = response.json()
            detail = error_data.get("message", detail)
        except ValueError:
            if response.text:
                detail = response.text
        status_code = 502 if response.status_code >= 500 else 400
        raise HTTPException(status_code=status_code, detail=detail)

    return response.json()


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        # NOWPayments часто присылает "...Z"
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _upsert_nowpayments_payment_from_create(
    db: Session,
    request_payload: dict,
    nowpayments_response: dict,
) -> None:
    payment_id = nowpayments_response.get("payment_id")
    if payment_id is None:
        return
    payment_id = str(payment_id)

    record = db.query(NowPaymentsPayment).filter(NowPaymentsPayment.payment_id == payment_id).first()
    if not record:
        record = NowPaymentsPayment(payment_id=payment_id)
        db.add(record)

    record.order_id = nowpayments_response.get("order_id") or request_payload.get("order_id")
    record.price_amount = nowpayments_response.get("price_amount") or request_payload.get("price_amount")
    record.price_currency = nowpayments_response.get("price_currency") or request_payload.get("price_currency")
    record.pay_amount = nowpayments_response.get("pay_amount")
    record.pay_currency = nowpayments_response.get("pay_currency") or request_payload.get("pay_currency")
    record.status = nowpayments_response.get("payment_status")
    record.expires_at = _parse_iso_datetime(nowpayments_response.get("expiration_estimate_date"))
    record.raw_create_response = json.dumps(nowpayments_response)

    db.commit()


def _upsert_nowpayments_payment_from_ipn(db: Session, payload: dict) -> None:
    payment_id = payload.get("payment_id")
    if payment_id is None:
        return
    payment_id = str(payment_id)

    record = db.query(NowPaymentsPayment).filter(NowPaymentsPayment.payment_id == payment_id).first()
    if not record:
        record = NowPaymentsPayment(payment_id=payment_id)
        db.add(record)

    record.order_id = payload.get("order_id") or record.order_id
    record.status = payload.get("payment_status") or record.status
    if payload.get("price_amount") is not None:
        record.price_amount = payload.get("price_amount")
    if payload.get("price_currency") is not None:
        record.price_currency = payload.get("price_currency")
    if payload.get("pay_amount") is not None:
        record.pay_amount = payload.get("pay_amount")
    if payload.get("pay_currency") is not None:
        record.pay_currency = payload.get("pay_currency")
    record.raw_last_ipn = json.dumps(payload)

    db.commit()


def _store_ipn_event(
    db: Session,
    payload: dict,
    signature_header: str,
    signature_valid: bool,
) -> None:
    ev = NowPaymentsIpnEvent(
        payment_id=str(payload.get("payment_id")) if payload.get("payment_id") is not None else None,
        payment_status=payload.get("payment_status"),
        order_id=payload.get("order_id"),
        signature_valid=bool(signature_valid),
        signature_header=signature_header or None,
        payload_json=json.dumps(payload),
    )
    db.add(ev)
    db.commit()


def _apply_non_finished_status(db: Session, payment_id: str, order_id: Optional[str], status: str, payload: dict) -> None:
    # Обновляем существующую запись в payments (таблица приложения), если она уже есть
    db_payment = db.query(PaymentModel).filter(PaymentModel.transaction_id == str(payment_id)).first()
    booking = get_booking_by_payment(db, int(payment_id) if str(payment_id).isdigit() else 0, order_id)

    if db_payment:
        db_payment.payment_metadata = json.dumps(payload)
        normalized = (status or "").lower()
        if normalized in {"expired", "failed"}:
            db_payment.status = "failed"
        elif normalized == "refunded":
            db_payment.status = "refunded"
        else:
            db_payment.status = "pending"

    if booking:
        normalized = (status or "").lower()
        if normalized in {"expired", "failed"}:
            booking.payment_status = "failed"
        elif normalized == "refunded":
            booking.payment_status = "refunded"
            booking.status = "pending"
            booking.payment_date = None
        else:
            booking.payment_status = "pending"

    # Product purchase status update
    pp_id = parse_product_purchase_id(order_id)
    if pp_id:
        purchase = db.query(ProductPurchase).filter(ProductPurchase.id == pp_id).first()
        if purchase:
            purchase.status = status or purchase.status
            purchase.raw_last_ipn = json.dumps(payload)

    db.commit()


def apply_finished_status(
    db: Session,
    payment_id: int,
    order_id: Optional[str],
    payload: dict,
) -> None:
    db_payment = db.query(PaymentModel).filter(PaymentModel.transaction_id == str(payment_id)).first()
    booking = get_booking_by_payment(db, payment_id, order_id)

    if db_payment:
        if db_payment.status != "completed":
            db_payment.status = "completed"
            db_payment.completed_at = datetime.now()
        db_payment.payment_metadata = json.dumps(payload)
    elif booking:
        db_payment = PaymentModel(
            booking_id=booking.id,
            user_id=booking.user_id,
            webinar_id=booking.webinar_id,
            amount=payload.get("price_amount") or booking.amount or 0,
            currency=(payload.get("price_currency") or "USD").upper(),
            payment_method="crypto",
            payment_provider="nowpayments",
            transaction_id=str(payment_id),
            status="completed",
            payment_metadata=json.dumps(payload),
            completed_at=datetime.now(),
        )
        db.add(db_payment)

    if booking:
        booking.payment_status = "paid"
        booking.status = "confirmed"
        booking.payment_date = datetime.now()
        booking.payment_id = str(payment_id)
        if payload.get("price_amount"):
            booking.amount = payload.get("price_amount")

        # Standalone payment (not webinar): выдаём роль/доступ пользователю
        if (booking.type or "").lower() == "payment":
            exists = (
                db.query(UserEntitlement)
                .filter(UserEntitlement.user_id == booking.user_id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
                .first()
            )
            if not exists:
                db.add(UserEntitlement(user_id=booking.user_id, code=PAID_ACCESS_ENTITLEMENT))

    # Product purchase: выдаём доступ по order_id product-<id>
    pp_id = parse_product_purchase_id(order_id)
    if pp_id:
        purchase = db.query(ProductPurchase).filter(ProductPurchase.id == pp_id).first()
        if purchase:
            purchase.status = "finished"
            purchase.nowpayments_payment_id = str(payment_id)
            purchase.raw_last_ipn = json.dumps(payload)
            if payload.get("pay_address"):
                purchase.pay_address = payload.get("pay_address")
            if payload.get("pay_amount") is not None:
                try:
                    purchase.pay_amount = float(payload.get("pay_amount"))
                except Exception:
                    pass
            exists2 = (
                db.query(UserEntitlement)
                .filter(UserEntitlement.user_id == purchase.user_id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
                .first()
            )
            if not exists2:
                db.add(UserEntitlement(user_id=purchase.user_id, code=PAID_ACCESS_ENTITLEMENT))

    db.commit()


def get_currencies_from_nowpayments():
    # NOWPayments: GET /v1/currencies
    return nowpayments_request("GET", "/currencies")


@router.get("/currencies")
def currencies():
    return get_currencies_from_nowpayments()


@router.post("/create", response_model=CreatePaymentResponse)
def create_payment(payload: CreatePaymentRequest, db: Session = Depends(get_db)):
    started = time.monotonic()
    ipn_callback_url = os.getenv("NOWPAYMENTS_IPN_CALLBACK_URL")
    if not ipn_callback_url:
        raise HTTPException(status_code=500, detail="NOWPAYMENTS_IPN_CALLBACK_URL is not configured")

    # Вебинары бесплатные — оплата вебинаров отключена
    booking_id = parse_booking_id(payload.order_id)
    if booking_id:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking and (booking.type or "").lower() == "webinar":
            raise HTTPException(status_code=400, detail="Вебинары бесплатные — оплата не требуется")

    # NOWPayments expects fiat-like price_currency (usd/eur). Some clients may send "usdt" by mistake.
    # To keep backward compatibility and avoid "Can not get estimate from USDT to USDTTRC20",
    # normalize USDT price_currency -> USD when paying in USDT TRC20.
    price_currency = (payload.price_currency or "").strip().lower()
    pay_currency = (payload.pay_currency or "").strip().lower()
    if price_currency in {"usdt", "usdttrc20"} and pay_currency.startswith("usdt"):
        price_currency = "usd"

    request_payload = {
        "price_amount": payload.amount,
        "price_currency": price_currency,
        "pay_currency": payload.pay_currency,
        "order_id": payload.order_id,
        "order_description": payload.order_description,
        "ipn_callback_url": ipn_callback_url,
    }
    request_payload = {key: value for key, value in request_payload.items() if value is not None}
    logger.info("nowpayments.create start order_id=%s amount=%s pay_currency=%s", payload.order_id, payload.amount, payload.pay_currency)
    data = nowpayments_request("POST", "/payment", json=request_payload)
    logger.info("nowpayments.create ok order_id=%s payment_id=%s took_ms=%s", payload.order_id, data.get("payment_id"), int((time.monotonic() - started) * 1000))

    response = CreatePaymentResponse(
        payment_id=data["payment_id"],
        pay_address=data.get("pay_address"),
        pay_amount=data.get("pay_amount"),
        pay_currency=data.get("pay_currency"),
    )

    if booking_id:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            db_payment = PaymentModel(
                booking_id=booking.id,
                user_id=booking.user_id,
                webinar_id=booking.webinar_id,
                amount=payload.amount,
                currency=(payload.price_currency or "USD").upper(),
                payment_method="crypto",
                payment_provider="nowpayments",
                transaction_id=str(data["payment_id"]),
                status="pending",
                payment_metadata=json.dumps(data),
            )
            db.add(db_payment)
            booking.payment_status = "pending"
            booking.payment_id = str(data["payment_id"])
            booking.amount = payload.amount
            db.commit()

    return response




@router.get("/status/{payment_id}", response_model=PaymentStatusMinimal)
def check_payment_status(payment_id: int, db: Session = Depends(get_db)):
    data = nowpayments_request("GET", f"/payment/{payment_id}")
    payment_status = data.get("payment_status")
    # Важно: доступ/подписку выдаём только по IPN ("finished"), а не по GET.
    if data.get("payment_id"):
        try:
            record = (
                db.query(NowPaymentsPayment)
                .filter(NowPaymentsPayment.payment_id == str(data.get("payment_id")))
                .first()
            )
            if not record:
                record = NowPaymentsPayment(payment_id=str(data.get("payment_id")))
                db.add(record)
            record.status = data.get("payment_status") or record.status
            record.raw_last_status_response = json.dumps(data)
            record.expires_at = _parse_iso_datetime(data.get("expiration_estimate_date")) or record.expires_at
            if data.get("pay_amount") is not None:
                record.pay_amount = data.get("pay_amount")
            if data.get("pay_currency") is not None:
                record.pay_currency = data.get("pay_currency")
            if data.get("price_amount") is not None:
                record.price_amount = data.get("price_amount")
            if data.get("price_currency") is not None:
                record.price_currency = data.get("price_currency")
            if data.get("order_id") is not None:
                record.order_id = data.get("order_id")
            db.commit()
        except Exception:
            # не ломаем статус-эндпоинт из-за проблем записи в БД
            pass
    return PaymentStatusMinimal(payment_id=payment_id, payment_status=payment_status)


@router.get("/payment/{payment_id}")
def get_payment_full(payment_id: int, db: Session = Depends(get_db)):
    # Полный ответ NOWPayments, чтобы фронт мог показать pay_address/pay_amount.
    data = nowpayments_request("GET", f"/payment/{payment_id}")
    try:
        record = db.query(NowPaymentsPayment).filter(NowPaymentsPayment.payment_id == str(payment_id)).first()
        if not record:
            record = NowPaymentsPayment(payment_id=str(payment_id))
            db.add(record)
        record.status = data.get("payment_status") or record.status
        record.raw_last_status_response = json.dumps(data)
        record.expires_at = _parse_iso_datetime(data.get("expiration_estimate_date")) or record.expires_at
        if data.get("pay_amount") is not None:
            record.pay_amount = data.get("pay_amount")
        if data.get("pay_currency") is not None:
            record.pay_currency = data.get("pay_currency")
        if data.get("price_amount") is not None:
            record.price_amount = data.get("price_amount")
        if data.get("price_currency") is not None:
            record.price_currency = data.get("price_currency")
        if data.get("order_id") is not None:
            record.order_id = data.get("order_id")
        db.commit()
    except Exception:
        pass
    return data


@router.post("/ipn")
async def nowpayments_ipn(request: Request, db: Session = Depends(get_db)):
    secret = os.getenv("NOWPAYMENTS_IPN_SECRET", "")
    signature = request.headers.get("X-NOWPayments-Sig", "")
    raw_body = await request.body()
    try:
        payload = json.loads(raw_body.decode("utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    signature_valid = verify_nowpayments_signature(payload, signature, secret)
    logger.info(
        "ipn received payment_id=%s status=%s signature_valid=%s",
        payload.get("payment_id"),
        payload.get("payment_status"),
        signature_valid,
    )
    if os.getenv("DEBUG_NOWPAYMENTS_IPN") == "1":
        logger.info("ipn payload: %s", payload)
    _store_ipn_event(db, payload, signature, signature_valid)

    if not signature_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    payment_id = payload.get("payment_id")
    if payment_id is None:
        raise HTTPException(status_code=400, detail="Missing payment_id")

    payment_status = payload.get("payment_status")
    if not payment_status:
        raise HTTPException(status_code=400, detail="Missing payment_status")

    _upsert_nowpayments_payment_from_ipn(db, payload)

    normalized = str(payment_status).lower()
    if normalized == "finished":
        # ЕДИНСТВЕННЫЙ источник истины для выдачи доступа — IPN finished
        apply_finished_status(db, int(payment_id) if str(payment_id).isdigit() else 0, payload.get("order_id"), payload)
    else:
        # waiting / confirming / expired / failed / refunded и т.д.
        _apply_non_finished_status(db, str(payment_id), payload.get("order_id"), normalized, payload)

    return {"status": "ok"}
