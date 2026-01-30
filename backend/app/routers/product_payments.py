from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.product_purchase import ProductPurchase
from app.models.user import User
from app.schemas.product_purchase import ProductPaymentCreateRequest, ProductPaymentCreateResponse
from app.routers.nowpayments import nowpayments_request
from app.utils.telegram_webapp import resolve_admin_telegram_id, verify_telegram_webapp_init_data


logger = logging.getLogger("product_payments")
router = APIRouter(prefix="/product-payments", tags=["product-payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create", response_model=ProductPaymentCreateResponse)
def create_product_payment(
    payload: ProductPaymentCreateRequest,
    request: Request,
    admin_telegram_id: int | None = None,
    response: Response | None = None,
    db: Session = Depends(get_db),
):
    """
    Create NOWPayments invoice for a product purchase.
    Not related to bookings/webinars.
    Requires Telegram WebApp initData header (X-Telegram-Init-Data) to identify user.
    """
    ipn_callback_url = os.getenv("NOWPAYMENTS_IPN_CALLBACK_URL")
    if not ipn_callback_url:
        raise HTTPException(status_code=500, detail="NOWPAYMENTS_IPN_CALLBACK_URL is not configured")

    # Primary: Telegram WebApp initData header (X-Telegram-Init-Data)
    # Fallback: telegram_init_data in JSON body (some WebViews strip custom headers)
    # Optional for server-side testing: X-Internal-Key + admin_telegram_id query
    try:
        telegram_id = int(resolve_admin_telegram_id(request, admin_telegram_id, allow_internal=True))
    except HTTPException as exc:
        # Safe debug: do not log initData contents, only presence/length + reason.
        if exc.status_code == 401:
            hdr_len = len((request.headers.get("X-Telegram-Init-Data") or "").strip())
            body_len = len((payload.telegram_init_data or "").strip())
            logger.info(
                "product_payments.telegram_auth_failed detail=%s header_len=%s body_len=%s",
                getattr(exc, "detail", "unauthorized"),
                hdr_len,
                body_len,
            )
        if exc.status_code == 401 and payload.telegram_init_data:
            user = verify_telegram_webapp_init_data(payload.telegram_init_data, os.getenv("TELEGRAM_BOT_TOKEN", ""))
            telegram_id = int(user["id"])
        else:
            raise
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        # Minimal create; real fields can be filled by /users/telegram/{id}
        user = User(telegram_id=telegram_id, username=None, first_name=None, last_name=None, photo_url=None)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Idempotency / anti-duplicate:
    # If WebView re-mounts and re-sends create, return a recent pending purchase for this user.
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
        recent = (
            db.query(ProductPurchase)
            .filter(
                ProductPurchase.user_id == user.id,
                ProductPurchase.created_at >= cutoff,
                ProductPurchase.status.in_(["pending", "waiting", "confirming"]),
            )
            .order_by(ProductPurchase.id.desc())
            .first()
        )
        if recent and recent.nowpayments_payment_id and recent.pay_address and recent.pay_amount:
            resp_obj = ProductPaymentCreateResponse(
                purchase_id=recent.id,
                order_id=recent.order_id,
                payment_id=int(recent.nowpayments_payment_id),
                pay_address=recent.pay_address,
                pay_amount=recent.pay_amount,
                pay_currency=recent.pay_currency,
                payment_status=recent.status,
                expiration_estimate_date=None,
                invoice_url=None,
            )
            # Provide critical values via headers too (so frontend can use without reading body).
            if response is not None:
                response.headers["X-Payment-Id"] = str(resp_obj.payment_id)
                response.headers["X-Pay-Address"] = resp_obj.pay_address or ""
                response.headers["X-Pay-Amount"] = str(resp_obj.pay_amount or "")
                response.headers["X-Pay-Currency"] = (resp_obj.pay_currency or "").lower()
            logger.info(
                "product_payments.create reuse purchase_id=%s payment_id=%s order_id=%s",
                recent.id,
                recent.nowpayments_payment_id,
                recent.order_id,
            )
            return resp_obj
    except Exception:
        # never block payment creation on idempotency logic
        pass

    # Normalize price_currency for NOWPayments (see earlier issue with USDT -> USDTTRC20 estimate)
    price_currency = (payload.price_currency or "").strip().lower()
    pay_currency = (payload.pay_currency or "").strip().lower()
    if price_currency in {"usdt", "usdttrc20"} and pay_currency.startswith("usdt"):
        price_currency = "usd"

    purchase = ProductPurchase(
        user_id=user.id,
        order_id="product-pending",
        amount_usd=float(payload.amount),
        price_currency=price_currency,
        pay_currency=pay_currency or "usdttrc20",
        status="pending",
    )
    db.add(purchase)
    db.flush()  # get purchase.id without committing yet
    purchase.order_id = f"product-{purchase.id}"

    request_payload = {
        "price_amount": float(payload.amount),
        "price_currency": price_currency,
        "pay_currency": pay_currency or "usdttrc20",
        "order_id": purchase.order_id,
        "order_description": payload.order_description or "Product purchase",
        "ipn_callback_url": ipn_callback_url,
    }
    request_payload = {k: v for k, v in request_payload.items() if v is not None}

    logger.info("product_payments.create start order_id=%s user_tg=%s", purchase.order_id, telegram_id)
    data = nowpayments_request("POST", "/payment", json=request_payload)

    # Diagnostics: what we got from NOWPayments and what we return to frontend (no secrets).
    try:
        logger.info(
            "product_payments.create nowpayments payment_id=%s pay_address=%s pay_amount=%s pay_currency=%s status=%s invoice_url=%s keys=%s",
            data.get("payment_id"),
            (data.get("pay_address") or "")[:12] + ("…" if data.get("pay_address") else ""),
            data.get("pay_amount"),
            data.get("pay_currency"),
            data.get("payment_status"),
            data.get("invoice_url") or data.get("payment_url") or None,
            sorted(list(data.keys()))[:40],
        )
    except Exception:
        pass

    purchase.nowpayments_payment_id = str(data.get("payment_id")) if data.get("payment_id") is not None else None
    purchase.pay_address = data.get("pay_address")
    purchase.pay_amount = data.get("pay_amount")
    purchase.raw_create_response = json.dumps(data)
    purchase.status = str(data.get("payment_status") or "waiting")

    db.commit()
    db.refresh(purchase)

    resp_obj = ProductPaymentCreateResponse(
        purchase_id=purchase.id,
        order_id=purchase.order_id,
        payment_id=int(data["payment_id"]),
        pay_address=data.get("pay_address"),
        pay_amount=data.get("pay_amount"),
        pay_currency=data.get("pay_currency"),
        payment_status=data.get("payment_status"),
        expiration_estimate_date=data.get("expiration_estimate_date"),
        invoice_url=data.get("invoice_url") or data.get("payment_url"),
    )

    # Provide critical values via headers too (so frontend can use without reading body).
    if response is not None:
        response.headers["X-Payment-Id"] = str(resp_obj.payment_id)
        response.headers["X-Pay-Address"] = resp_obj.pay_address or ""
        response.headers["X-Pay-Amount"] = str(resp_obj.pay_amount or "")
        response.headers["X-Pay-Currency"] = (resp_obj.pay_currency or "").lower()

    logger.info(
        "product_payments.create response_keys=%s",
        ["purchase_id", "order_id", "payment_id", "pay_address", "pay_amount", "pay_currency", "payment_status", "expiration_estimate_date", "invoice_url"],
    )
    return resp_obj

