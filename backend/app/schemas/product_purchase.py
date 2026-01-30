from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductPaymentCreateRequest(BaseModel):
    amount: float = Field(..., gt=0)
    price_currency: str = Field(default="usd", min_length=2)
    pay_currency: str = Field(default="usdttrc20", min_length=2)
    order_description: Optional[str] = Field(default=None, max_length=255)
    # Fallback for Telegram WebViews that don't send custom headers reliably.
    telegram_init_data: Optional[str] = Field(default=None, max_length=4096)


class ProductPaymentCreateResponse(BaseModel):
    purchase_id: int
    order_id: str
    payment_id: int
    pay_address: Optional[str] = None
    pay_amount: Optional[float] = None
    pay_currency: Optional[str] = None
    # Optional NOWPayments fields (UI can use them immediately)
    payment_status: Optional[str] = None
    expiration_estimate_date: Optional[str] = None
    invoice_url: Optional[str] = None


class ProductPurchaseResponse(BaseModel):
    id: int
    order_id: str
    amount_usd: float
    price_currency: str
    pay_currency: str
    status: str
    nowpayments_payment_id: Optional[str] = None
    pay_address: Optional[str] = None
    pay_amount: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

