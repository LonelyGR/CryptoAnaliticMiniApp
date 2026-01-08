from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.models.user import User
from app.models.admin import Admin
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


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
        user_dict = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": user.photo_url,
            "is_admin": admin is not None,
            "role": admin.role if admin else None
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
    
    # Создаем ответ с информацией об админстве
    user_dict = {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "photo_url": user.photo_url,
        "is_admin": admin is not None,
        "role": admin.role if admin else None
    }
    return user_dict


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем, является ли пользователь админом
    admin = db.query(Admin).filter(Admin.telegram_id == user.telegram_id).first()
    
    # Создаем ответ с информацией об админстве
    user_dict = {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "photo_url": user.photo_url,
        "is_admin": admin is not None,
        "role": admin.role if admin else None
    }
    return user_dict


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
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
        return existing_user
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/telegram/{telegram_id}", response_model=UserResponse)
def create_or_update_user_by_telegram(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    photo_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Создает или обновляет пользователя по telegram_id"""
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
        db.commit()
        db.refresh(existing_user)
    else:
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
    
    # Проверяем, является ли пользователь админом
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    
    # Создаем ответ с информацией об админстве
    user_dict = {
        "id": existing_user.id,
        "telegram_id": existing_user.telegram_id,
        "username": existing_user.username,
        "first_name": existing_user.first_name,
        "last_name": existing_user.last_name,
        "photo_url": existing_user.photo_url,
        "is_admin": admin is not None,
        "role": admin.role if admin else None
    }
    return user_dict

