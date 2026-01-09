from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    webinar_id = Column(Integer, ForeignKey("webinars.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(String, nullable=True)  # card, paypal, apple_pay, etc.
    payment_provider = Column(String, nullable=True)  # stripe, paypal, etc.
    transaction_id = Column(String, nullable=True)  # ID транзакции от платежной системы
    status = Column(String, default="pending")  # pending, completed, failed, refunded
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    payment_metadata = Column(Text, nullable=True)  # Дополнительные данные в JSON формате (metadata зарезервировано в SQLAlchemy)
