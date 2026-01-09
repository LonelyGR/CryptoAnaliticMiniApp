from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.models.booking import Booking
from app.models.user import User
from app.models.admin import Admin
from app.schemas.booking import BookingCreate, BookingResponse, BookingResponseAdmin, BookingResponseUpdate

router = APIRouter(prefix="/bookings", tags=["bookings"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_admin(telegram_id: int, db: Session) -> Admin:
    """Проверка, является ли пользователь админом"""
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора")
    return admin

@router.get("/", response_model=List[BookingResponse])
def get_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = db.query(Booking).offset(skip).limit(limit).all()
    return bookings

@router.get("/consultations", response_model=List[BookingResponseAdmin])
def get_consultations(
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить все консультации (только для администраторов)"""
    check_admin(admin_telegram_id, db)
    
    consultations = db.query(Booking).filter(
        Booking.type == "consultation"
    ).offset(skip).limit(limit).all()
    
    result = []
    for consultation in consultations:
        user = db.query(User).filter(User.id == consultation.user_id).first()
        consultation_dict = {
            "id": consultation.id,
            "user_id": consultation.user_id,
            "webinar_id": consultation.webinar_id,
            "type": consultation.type,
            "date": consultation.date,
            "time": consultation.time,
            "status": consultation.status,
            "topic": consultation.topic,
            "message": consultation.message,
            "admin_response": consultation.admin_response,
            "admin_id": consultation.admin_id,
            "user_telegram_id": user.telegram_id if user else None,
            "user_first_name": user.first_name if user else None,
            "user_username": user.username if user else None,
        }
        result.append(consultation_dict)
    
    return result

@router.get("/support-tickets", response_model=List[BookingResponseAdmin])
def get_support_tickets(
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить все обращения в поддержку (только для администраторов)"""
    check_admin(admin_telegram_id, db)
    
    support_tickets = db.query(Booking).filter(
        Booking.type == "support"
    ).offset(skip).limit(limit).all()
    
    result = []
    for ticket in support_tickets:
        user = db.query(User).filter(User.id == ticket.user_id).first()
        ticket_dict = {
            "id": ticket.id,
            "user_id": ticket.user_id,
            "webinar_id": ticket.webinar_id,
            "type": ticket.type,
            "date": ticket.date,
            "time": ticket.time,
            "status": ticket.status,
            "topic": ticket.topic,
            "message": ticket.message,
            "admin_response": ticket.admin_response,
            "admin_id": ticket.admin_id,
            "user_telegram_id": user.telegram_id if user else None,
            "user_first_name": user.first_name if user else None,
            "user_username": user.username if user else None,
        }
        result.append(ticket_dict)
    
    return result


@router.get("/user/{user_id}", response_model=List[BookingResponse])
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    return bookings


@router.get("/telegram/{telegram_id}", response_model=List[BookingResponse])
def get_user_bookings_by_telegram(telegram_id: int, db: Session = Depends(get_db)):
    """Получить записи пользователя по telegram_id"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        return []
    bookings = db.query(Booking).filter(Booking.user_id == user.id).all()
    return bookings


@router.post("/", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    db_booking = Booking(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Удалить тикет (только для администраторов)"""
    check_admin(admin_telegram_id, db)
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    return {"message": "Booking deleted successfully"}

@router.put("/{booking_id}/respond", response_model=BookingResponse)
def respond_to_consultation(
    booking_id: int,
    response: BookingResponseUpdate,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Ответить на консультацию или обращение в поддержку (только для администраторов)"""
    admin = check_admin(admin_telegram_id, db)
    
    # Получаем user_id админа из БД
    admin_user = db.query(User).filter(User.telegram_id == admin_telegram_id).first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.type not in ["consultation", "support"]:
        raise HTTPException(status_code=400, detail="This booking type does not support responses")
    
    # Обновляем ответ (используем admin_id из response, но проверяем что он правильный)
    booking.admin_response = response.admin_response
    booking.admin_id = admin_user.id
    booking.status = "answered"
    
    db.commit()
    db.refresh(booking)
    return booking

