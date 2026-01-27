from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text

from app.database import SessionLocal
from app.models.admin import Admin
from app.database import Base
from app.models import admin, booking, payment, post, referral_invite, user, webinar_material, webinar  # noqa: F401
from app.schemas.admin import AdminCreate, AdminResponse, AdminUpdate
from app.utils.telegram_webapp import resolve_admin_telegram_id

router = APIRouter(prefix="/admins", tags=["admins"])


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


def check_developer(telegram_id: int, db: Session) -> Admin:
    admin = check_admin(telegram_id, db)
    role = (admin.role or "").lower()
    if role not in ["разработчик", "developer", "владелец", "owner"]:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права разработчика")
    return admin


@router.get("/", response_model=List[AdminResponse])
def get_admins(
    request: Request,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Получить список всех админов (только для админов)"""
    requester_id = resolve_admin_telegram_id(request, admin_telegram_id)
    check_admin(requester_id, db)
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
def create_admin(
    request: Request,
    admin: AdminCreate,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    db: Session = Depends(get_db),
):
    """Создать нового админа (только для разработчика)"""
    requester_id = resolve_admin_telegram_id(request, admin_telegram_id)
    check_developer(requester_id, db)
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
def update_admin(
    request: Request,
    admin_id: int,
    admin: AdminUpdate,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    db: Session = Depends(get_db),
):
    """Обновить админа (изменить роль) (только для разработчика)"""
    requester_id = resolve_admin_telegram_id(request, admin_telegram_id)
    check_developer(requester_id, db)
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db_admin.role = admin.role
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.delete("/{admin_id}")
def delete_admin(
    request: Request,
    admin_id: int,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    db: Session = Depends(get_db),
):
    """Удалить админа (только для разработчика)"""
    requester_id = resolve_admin_telegram_id(request, admin_telegram_id)
    check_developer(requester_id, db)
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    db.delete(admin)
    db.commit()
    return {"message": "Admin deleted successfully"}


@router.post("/clear-db")
def clear_database(
    request: Request,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    db: Session = Depends(get_db),
):
    """Полная очистка базы данных (только для разработчика)"""
    requester_id = resolve_admin_telegram_id(request, admin_telegram_id)
    check_developer(requester_id, db)

    db.execute(text("PRAGMA foreign_keys=OFF"))
    total_deleted = 0
    for table in reversed(Base.metadata.sorted_tables):
        result = db.execute(table.delete())
        deleted = result.rowcount if result.rowcount is not None else 0
        total_deleted += deleted
    db.commit()
    db.execute(text("PRAGMA foreign_keys=ON"))
    return {"message": "Database cleared", "deleted_rows": total_deleted}


@router.post("/clear-data")
def clear_selected_data(
    request: Request,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    targets: List[str] = Query(...),
    db: Session = Depends(get_db)
):
    """Удалить выбранные данные (только для разработчика)"""
    requester_id = resolve_admin_telegram_id(request, admin_telegram_id)
    check_developer(requester_id, db)

    if not targets:
        raise HTTPException(status_code=400, detail="Не указаны данные для удаления")

    targets_set = {target.strip() for target in targets if target and target.strip()}
    allowed_tables = {table.name for table in Base.metadata.sorted_tables}
    unknown_targets = sorted(targets_set - allowed_tables)
    if unknown_targets:
        raise HTTPException(
            status_code=400,
            detail=f"Неизвестные таблицы для удаления: {', '.join(unknown_targets)}"
        )

    db.execute(text("PRAGMA foreign_keys=OFF"))
    total_deleted = 0
    details = []
    for table in reversed(Base.metadata.sorted_tables):
        if table.name not in targets_set:
            continue
        result = db.execute(table.delete())
        deleted = result.rowcount if result.rowcount is not None else 0
        total_deleted += deleted
        details.append({"table": table.name, "deleted": deleted})
    db.commit()
    db.execute(text("PRAGMA foreign_keys=ON"))
    return {"message": "Selected data cleared", "deleted_rows": total_deleted, "details": details}
