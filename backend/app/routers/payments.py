from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.webinar import Webinar
from app.models.admin import Admin
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.utils.telegram_webapp import resolve_admin_telegram_id

router = APIRouter(prefix="/payments", tags=["payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_admin_access(request: Request, admin_telegram_id: int | None, db: Session) -> Admin:
    """Проверка прав администратора"""
    requester_id = resolve_admin_telegram_id(request, admin_telegram_id)
    admin = db.query(Admin).filter(Admin.telegram_id == requester_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора")
    return admin


@router.post("/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    """Создать платеж (legacy endpoint, используется для бронирований)"""
    # Проверяем, что booking существует
    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db_payment = Payment(**payment.model_dump())
    db_payment.user_id = booking.user_id
    db_payment.webinar_id = booking.webinar_id
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return db_payment


@router.get("/booking/{booking_id}", response_model=List[PaymentResponse])
def get_payments_by_booking(booking_id: int, db: Session = Depends(get_db)):
    """Получить все платежи по booking_id"""
    payments = db.query(Payment).filter(Payment.booking_id == booking_id).all()
    return payments


@router.get("/user/{user_id}", response_model=List[PaymentResponse])
def get_user_payments(user_id: int, db: Session = Depends(get_db)):
    """Получить все платежи пользователя"""
    payments = db.query(Payment).filter(Payment.user_id == user_id).all()
    return payments


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    request: Request,
    payment_id: int,
    payment_update: PaymentUpdate,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    db: Session = Depends(get_db)
):
    """Обновить статус платежа (только для администраторов)"""
    check_admin_access(request, admin_telegram_id, db)
    
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Обновляем статус платежа
    for key, value in payment_update.model_dump(exclude_unset=True).items():
        setattr(db_payment, key, value)
    
    # Если платеж завершен, обновляем booking
    if payment_update.status == "completed":
        booking = db.query(Booking).filter(Booking.id == db_payment.booking_id).first()
        if booking:
            booking.payment_status = "paid"
            booking.status = "confirmed"
            booking.amount = db_payment.amount
            booking.payment_id = db_payment.transaction_id
            from datetime import datetime
            booking.payment_date = datetime.now()
    
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.get("/", response_model=List[PaymentResponse])
def get_all_payments(
    request: Request,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить все платежи (только для администраторов)"""
    check_admin_access(request, admin_telegram_id, db)
    payments = db.query(Payment).offset(skip).limit(limit).all()
    return payments
