from fastapi import APIRouter, Depends, HTTPException, Body, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.models.user import User
from app.models.admin import Admin
from app.models.user_entitlement import UserEntitlement
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.utils.telegram_webapp import resolve_admin_telegram_id

router = APIRouter(prefix="/users", tags=["users"])

PAID_ACCESS_ENTITLEMENT = "paid_access"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    
    # Добавляем информацию об админстве для каждого пользователя
    result = []
    for user in users:
        admin = db.query(Admin).filter(Admin.telegram_id == user.telegram_id).first()
        has_paid_access = (
            db.query(UserEntitlement)
            .filter(UserEntitlement.user_id == user.id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
            .first()
            is not None
        )
        user_dict = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": user.photo_url,
            "referral_code": user.referral_code,
            "referred_by_telegram_id": user.referred_by_telegram_id,
            "is_blocked": user.is_blocked,
            "is_admin": admin is not None,
            "role": admin.role if admin else None,
            "client_role": "member" if has_paid_access else None,
            "has_paid_access": has_paid_access,
        }
        result.append(user_dict)
    return result


@router.get("/telegram/{telegram_id}", response_model=UserResponse)
def get_user_by_telegram_id(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем, является ли пользователь админом
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    has_paid_access = (
        db.query(UserEntitlement)
        .filter(UserEntitlement.user_id == user.id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
        .first()
        is not None
    )
    
    # Создаем ответ с информацией об админстве
    user_dict = {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "photo_url": user.photo_url,
        "referral_code": user.referral_code,
        "referred_by_telegram_id": user.referred_by_telegram_id,
        "is_blocked": user.is_blocked,
        "is_admin": admin is not None,
        "role": admin.role if admin else None,
        "client_role": "member" if has_paid_access else None,
        "has_paid_access": has_paid_access,
    }
    return user_dict


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем, является ли пользователь админом
    admin = db.query(Admin).filter(Admin.telegram_id == user.telegram_id).first()
    has_paid_access = (
        db.query(UserEntitlement)
        .filter(UserEntitlement.user_id == user.id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
        .first()
        is not None
    )
    
    # Создаем ответ с информацией об админстве
    user_dict = {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "photo_url": user.photo_url,
        "referral_code": user.referral_code,
        "referred_by_telegram_id": user.referred_by_telegram_id,
        "is_blocked": user.is_blocked,
        "is_admin": admin is not None,
        "role": admin.role if admin else None,
        "client_role": "member" if has_paid_access else None,
        "has_paid_access": has_paid_access,
    }
    return user_dict


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Создает или обновляет пользователя. Если пользователь с таким telegram_id уже существует, обновляет его данные."""
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.telegram_id == user.telegram_id).first()
    if existing_user:
        # Обновляем данные пользователя если они изменились
        if user.username is not None:
            existing_user.username = user.username
        if user.first_name is not None:
            existing_user.first_name = user.first_name
        if user.last_name is not None:
            existing_user.last_name = user.last_name
        if user.photo_url is not None:
            existing_user.photo_url = user.photo_url
        db.commit()
        db.refresh(existing_user)
        
        # Проверяем, является ли пользователь админом
        admin = db.query(Admin).filter(Admin.telegram_id == existing_user.telegram_id).first()
        has_paid_access = (
            db.query(UserEntitlement)
            .filter(UserEntitlement.user_id == existing_user.id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
            .first()
            is not None
        )
        return {
            "id": existing_user.id,
            "telegram_id": existing_user.telegram_id,
            "username": existing_user.username,
            "first_name": existing_user.first_name,
            "last_name": existing_user.last_name,
            "photo_url": existing_user.photo_url,
            "referral_code": existing_user.referral_code,
            "referred_by_telegram_id": existing_user.referred_by_telegram_id,
            "is_blocked": existing_user.is_blocked,
            "is_admin": admin is not None,
            "role": admin.role if admin else None,
            "client_role": "member" if has_paid_access else None,
            "has_paid_access": has_paid_access,
        }
    
    # Создаем нового пользователя
    try:
        db_user = User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Проверяем, является ли пользователь админом
        admin = db.query(Admin).filter(Admin.telegram_id == db_user.telegram_id).first()
        has_paid_access = (
            db.query(UserEntitlement)
            .filter(UserEntitlement.user_id == db_user.id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
            .first()
            is not None
        )
        return {
            "id": db_user.id,
            "telegram_id": db_user.telegram_id,
            "username": db_user.username,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "photo_url": db_user.photo_url,
            "referral_code": db_user.referral_code,
            "referred_by_telegram_id": db_user.referred_by_telegram_id,
            "is_blocked": db_user.is_blocked,
            "is_admin": admin is not None,
            "role": admin.role if admin else None,
            "client_role": "member" if has_paid_access else None,
            "has_paid_access": has_paid_access,
        }
    except Exception as e:
        db.rollback()
        # Если возникла ошибка UNIQUE constraint, значит пользователь был создан между проверкой и вставкой
        # Повторно проверяем и возвращаем существующего пользователя
        existing_user = db.query(User).filter(User.telegram_id == user.telegram_id).first()
        if existing_user:
            # Обновляем данные пользователя
            if user.username is not None:
                existing_user.username = user.username
            if user.first_name is not None:
                existing_user.first_name = user.first_name
            if user.last_name is not None:
                existing_user.last_name = user.last_name
            if user.photo_url is not None:
                existing_user.photo_url = user.photo_url
            db.commit()
            db.refresh(existing_user)
            
            admin = db.query(Admin).filter(Admin.telegram_id == existing_user.telegram_id).first()
            has_paid_access = (
                db.query(UserEntitlement)
                .filter(UserEntitlement.user_id == existing_user.id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
                .first()
                is not None
            )
            return {
                "id": existing_user.id,
                "telegram_id": existing_user.telegram_id,
                "username": existing_user.username,
                "first_name": existing_user.first_name,
                "last_name": existing_user.last_name,
                "photo_url": existing_user.photo_url,
                "referral_code": existing_user.referral_code,
                "referred_by_telegram_id": existing_user.referred_by_telegram_id,
                "is_blocked": existing_user.is_blocked,
                "is_admin": admin is not None,
                "role": admin.role if admin else None,
                "client_role": "member" if has_paid_access else None,
                "has_paid_access": has_paid_access,
            }
        # Если пользователь все еще не найден, пробрасываем ошибку
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")


@router.post("/telegram/{telegram_id}", response_model=UserResponse)
def create_or_update_user_by_telegram(
    telegram_id: int,
    user_data: Optional[UserUpdate] = Body(None),
    db: Session = Depends(get_db)
):
    """Создает или обновляет пользователя по telegram_id. Если пользователь уже существует, обновляет его данные."""
    # Если данные переданы в body, используем их
    if user_data:
        username = user_data.username
        first_name = user_data.first_name
        last_name = user_data.last_name
        photo_url = user_data.photo_url
        is_blocked = user_data.is_blocked
    else:
        # Иначе используем значения по умолчанию
        username = None
        first_name = None
        last_name = None
        photo_url = None
        is_blocked = None
    
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if existing_user:
        # Обновляем данные пользователя
        if username is not None:
            existing_user.username = username
        if first_name is not None:
            existing_user.first_name = first_name
        if last_name is not None:
            existing_user.last_name = last_name
        if photo_url is not None:
            existing_user.photo_url = photo_url
        if is_blocked is not None:
            existing_user.is_blocked = is_blocked
        db.commit()
        db.refresh(existing_user)
    else:
        # Создаем нового пользователя с обработкой возможной ошибки UNIQUE constraint
        try:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                photo_url=photo_url
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            existing_user = user
        except Exception as e:
            db.rollback()
            # Если возникла ошибка UNIQUE constraint, значит пользователь был создан между проверкой и вставкой
            # Повторно проверяем и обновляем существующего пользователя
            existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if existing_user:
                if username is not None:
                    existing_user.username = username
                if first_name is not None:
                    existing_user.first_name = first_name
                if last_name is not None:
                    existing_user.last_name = last_name
                if photo_url is not None:
                    existing_user.photo_url = photo_url
            if is_blocked is not None:
                existing_user.is_blocked = is_blocked
                db.commit()
                db.refresh(existing_user)
            else:
                # Если пользователь все еще не найден, пробрасываем ошибку
                raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")
    
    # Проверяем, является ли пользователь админом
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    has_paid_access = (
        db.query(UserEntitlement)
        .filter(UserEntitlement.user_id == existing_user.id, UserEntitlement.code == PAID_ACCESS_ENTITLEMENT)
        .first()
        is not None
    )
    
    # Создаем ответ с информацией об админстве
    user_dict = {
        "id": existing_user.id,
        "telegram_id": existing_user.telegram_id,
        "username": existing_user.username,
        "first_name": existing_user.first_name,
        "last_name": existing_user.last_name,
        "photo_url": existing_user.photo_url,
        "referral_code": existing_user.referral_code,
        "referred_by_telegram_id": existing_user.referred_by_telegram_id,
        "is_blocked": existing_user.is_blocked,
        "is_admin": admin is not None,
        "role": admin.role if admin else None,
        "client_role": "member" if has_paid_access else None,
        "has_paid_access": has_paid_access,
    }
    return user_dict


@router.put("/{user_id}/block")
def update_user_block_status(
    request: Request,
    user_id: int,
    admin_telegram_id: int = Query(None, description="Telegram ID администратора (legacy)"),
    is_blocked: bool = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    requester_id = resolve_admin_telegram_id(request, admin_telegram_id)
    admin = db.query(Admin).filter(Admin.telegram_id == requester_id).first()
    if not admin or (admin.role or "").lower() not in ["разработчик", "developer", "владелец", "owner"]:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права разработчика")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = bool(is_blocked)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "is_blocked": user.is_blocked}

