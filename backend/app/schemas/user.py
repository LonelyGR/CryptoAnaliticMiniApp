from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_admin: Optional[bool] = False  # Статус администратора
    role: Optional[str] = None  # Должность (если админ)

    class Config:
        from_attributes = True

