from pydantic import BaseModel
from typing import Optional

class AdminBase(BaseModel):
    telegram_id: int
    role: str  # Должность

class AdminCreate(AdminBase):
    pass

class AdminUpdate(BaseModel):
    """Схема для обновления админа (только роль)"""
    role: str

class AdminResponse(AdminBase):
    id: int

    class Config:
        from_attributes = True

