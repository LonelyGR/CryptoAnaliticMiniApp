from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class ProductPurchase(Base):
    __tablename__ = "product_purchases"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # We send this to NOWPayments and later match IPN by order_id
    order_id = Column(String(120), nullable=False, unique=True, index=True)

    amount_usd = Column(Float, nullable=False)
    price_currency = Column(String(16), nullable=False, default="usd")
    pay_currency = Column(String(32), nullable=False, default="usdttrc20")

    status = Column(String(32), nullable=False, default="pending")  # pending/finished/failed/expired/refunded

    nowpayments_payment_id = Column(String(64), nullable=True, index=True)
    pay_address = Column(String(255), nullable=True)
    pay_amount = Column(Float, nullable=True)

    raw_create_response = Column(Text, nullable=True)
    raw_last_ipn = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("nowpayments_payment_id", name="uq_product_purchases_nowpayments_payment_id"),
    )

