from pydantic import BaseModel
from typing import Optional

class BookingBase(BaseModel):
    user_id: int
    type: str  # webinar или consultation
    date: str
    status: str = "active"

class BookingCreate(BookingBase):
    webinar_id: Optional[int] = None
    time: Optional[str] = None
    topic: Optional[str] = None
    message: Optional[str] = None

class BookingResponse(BookingBase):
    id: int
    webinar_id: Optional[int] = None
    time: Optional[str] = None
    topic: Optional[str] = None
    message: Optional[str] = None
    admin_response: Optional[str] = None
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None  # Имя админа, который ответил
    admin_role: Optional[str] = None  # Роль админа, который ответил
    payment_status: Optional[str] = "unpaid"
    amount: Optional[float] = None
    payment_id: Optional[str] = None
    payment_date: Optional[str] = None
    attended: Optional[int] = 0

    class Config:
        from_attributes = True

class BookingResponseAdmin(BookingResponse):
    """Расширенный ответ для админов с информацией о пользователе"""
    user_telegram_id: Optional[int] = None
    user_first_name: Optional[str] = None
    user_username: Optional[str] = None

class BookingResponseUpdate(BaseModel):
    """Схема для обновления ответа администратора"""
    admin_response: str
    admin_id: Optional[int] = None  # Опциональный, так как используется admin_telegram_id

