from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class CreatePaymentRequest(BaseModel):
    order_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    price_currency: str = Field(..., min_length=2)
    pay_currency: Optional[str] = Field(default=None, min_length=2)
    success_url: Optional[HttpUrl] = None
    order_description: Optional[str] = Field(default=None, max_length=255)


class CreatePaymentResponse(BaseModel):
    payment_id: int
    pay_address: Optional[str] = None
    pay_amount: Optional[float] = None
    pay_currency: Optional[str] = None


class PaymentStatusMinimal(BaseModel):
    payment_id: int
    payment_status: Optional[str] = None


class NowPaymentsPaymentCreateRequest(BaseModel):
    # ВАЖНО: без extra=forbid по требованию
    price_amount: float
    price_currency: str
    pay_currency: str
    order_id: str
    order_description: Optional[str] = None
    ipn_callback_url: Optional[str] = None
