from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    referral_code: Optional[str] = None
    referred_by_telegram_id: Optional[int] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    """Схема для обновления пользователя (без telegram_id, так как он в URL)"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    referral_code: Optional[str] = None
    referred_by_telegram_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    is_admin: Optional[bool] = False  # Статус администратора
    role: Optional[str] = None  # Должность (если админ)

    class Config:
        from_attributes = True

