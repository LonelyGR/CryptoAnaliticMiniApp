from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.models.webinar import Webinar
from app.models.admin import Admin
from app.schemas.webinar import WebinarCreate, WebinarResponse

router = APIRouter(prefix="/webinars", tags=["webinars"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_admin_access(admin_telegram_id: int = Query(..., description="Telegram ID администратора"), db: Session = Depends(get_db)):
    """Проверка прав администратора для создания вебинаров"""
    admin = db.query(Admin).filter(Admin.telegram_id == admin_telegram_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора для создания вебинаров")
    return admin


@router.get("/", response_model=List[WebinarResponse])
def get_webinars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех вебинаров (доступно всем)"""
    webinars = db.query(Webinar).offset(skip).limit(limit).all()
    return webinars


@router.get("/{webinar_id}", response_model=WebinarResponse)
def get_webinar(webinar_id: int, db: Session = Depends(get_db)):
    """Получить вебинар по ID (доступно всем)"""
    webinar = db.query(Webinar).filter(Webinar.id == webinar_id).first()
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    return webinar


@router.post("/", response_model=WebinarResponse)
def create_webinar(
    webinar: WebinarCreate,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Создать вебинар (только для администраторов)
    
    Требуется параметр: admin_telegram_id с Telegram ID администратора
    """
    # Проверяем права администратора
    admin = check_admin_access(admin_telegram_id, db)
    
    # Создаем вебинар
    db_webinar = Webinar(**webinar.model_dump())
    db.add(db_webinar)
    db.commit()
    db.refresh(db_webinar)
    return db_webinar


@router.put("/{webinar_id}", response_model=WebinarResponse)
def update_webinar(
    webinar_id: int,
    webinar: WebinarCreate,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Обновить вебинар (только для администраторов)
    
    Требуется параметр: admin_telegram_id с Telegram ID администратора
    """
    # Проверяем права администратора
    admin = check_admin_access(admin_telegram_id, db)
    
    # Находим вебинар
    db_webinar = db.query(Webinar).filter(Webinar.id == webinar_id).first()
    if not db_webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    
    # Обновляем данные
    for key, value in webinar.model_dump().items():
        setattr(db_webinar, key, value)
    
    db.commit()
    db.refresh(db_webinar)
    return db_webinar


@router.delete("/{webinar_id}")
def delete_webinar(
    webinar_id: int,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Удалить вебинар (только для администраторов)
    
    Требуется параметр: admin_telegram_id с Telegram ID администратора
    При удалении вебинара также удаляются все связанные бронирования
    """
    # Проверяем права администратора
    admin = check_admin_access(admin_telegram_id, db)
    
    # Находим вебинар
    db_webinar = db.query(Webinar).filter(Webinar.id == webinar_id).first()
    if not db_webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    
    # Импортируем Booking для удаления связанных записей
    from app.models.booking import Booking
    
    # Удаляем все бронирования, связанные с этим вебинаром
    bookings_count = db.query(Booking).filter(Booking.webinar_id == webinar_id).delete()
    
    # Удаляем вебинар
    db.delete(db_webinar)
    db.commit()
    return {
        "message": "Webinar deleted successfully",
        "deleted_bookings": bookings_count
    }

