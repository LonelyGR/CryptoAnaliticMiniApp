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

    class Config:
        from_attributes = True

