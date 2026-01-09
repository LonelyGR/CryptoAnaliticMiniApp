from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    booking_id: int
    amount: float
    currency: str = "USD"
    payment_method: Optional[str] = None
    payment_provider: Optional[str] = None

class PaymentCreate(PaymentBase):
    transaction_id: Optional[str] = None
    payment_metadata: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    webinar_id: Optional[int] = None
    transaction_id: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentUpdate(BaseModel):
    status: str
    transaction_id: Optional[str] = None
    completed_at: Optional[datetime] = None
