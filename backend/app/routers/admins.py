from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminResponse, AdminUpdate

router = APIRouter(prefix="/admins", tags=["admins"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close


def check_admin(telegram_id: int, db: Session) -> Admin:
    """Проверка, является ли пользователь админом"""
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора")
    return admin


@router.get("/", response_model=List[AdminResponse])
def get_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех админов (только для админов)"""
    admins = db.query(Admin).offset(skip).limit(limit).all()
    return admins


@router.get("/telegram/{telegram_id}", response_model=AdminResponse)
def get_admin_by_telegram_id(telegram_id: int, db: Session = Depends(get_db)):
    """Получить админа по Telegram ID"""
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


@router.get("/check/{telegram_id}")
def check_admin_status(telegram_id: int, db: Session = Depends(get_db)):
    """Проверить, является ли пользователь админом"""
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if admin:
        return {
            "is_admin": True,
            "admin_id": admin.id,
            "telegram_id": admin.telegram_id,
            "role": admin.role
        }
    return {"is_admin": False}


@router.post("/", response_model=AdminResponse)
def create_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    """Создать нового админа"""
    # Проверяем, существует ли админ
    existing_admin = db.query(Admin).filter(Admin.telegram_id == admin.telegram_id).first()
    if existing_admin:
        # Обновляем должность если изменилась
        existing_admin.role = admin.role
        db.commit()
        db.refresh(existing_admin)
        return existing_admin
    
    db_admin = Admin(**admin.model_dump())
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin


@router.put("/{admin_id}", response_model=AdminResponse)
def update_admin(admin_id: int, admin: AdminUpdate, db: Session = Depends(get_db)):
    """Обновить админа (изменить роль)"""
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db_admin.role = admin.role
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.delete("/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    """Удалить админа"""
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    db.delete(admin)
    db.commit()
    return {"message": "Admin deleted successfully"}
