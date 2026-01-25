from sqlalchemy import Column, DateTime, Float, String, Text
from sqlalchemy.sql import func

from app.database import Base


class NowPaymentsPayment(Base):
    __tablename__ = "nowpayments_payments"

    # NOWPayments payment_id (приходит строкой в ответах)
    payment_id = Column(String, primary_key=True)

    order_id = Column(String, nullable=True, index=True)

    price_amount = Column(Float, nullable=True)
    price_currency = Column(String, nullable=True)

    pay_amount = Column(Float, nullable=True)
    pay_currency = Column(String, nullable=True)

    status = Column(String, nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    raw_create_response = Column(Text, nullable=True)
    raw_last_status_response = Column(Text, nullable=True)
    raw_last_ipn = Column(Text, nullable=True)

