from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    webinar_id = Column(Integer, ForeignKey("webinars.id"), nullable=True)  # ID вебинара, если это запись на вебинар
    type = Column(String)  # webinar или consultation
    date = Column(String)  # Дата записи
    time = Column(String, nullable=True)  # Время для консультаций
    status = Column(String, default="pending")  # pending, confirmed, paid, cancelled, completed
    topic = Column(String, nullable=True)  # Тема для консультаций
    message = Column(Text, nullable=True)  # Дополнительное сообщение от пользователя
    admin_response = Column(Text, nullable=True)  # Ответ администратора на консультацию
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ID админа, который ответил
    payment_status = Column(String, default="unpaid")  # unpaid, pending, paid, failed, refunded
    amount = Column(Float, nullable=True)  # Сумма оплаты
    payment_id = Column(String, nullable=True)  # ID платежа от платежной системы
    payment_date = Column(DateTime(timezone=True), nullable=True)  # Дата оплаты
    reminder_sent_24h = Column(Integer, default=0)  # Отправлено напоминание за 24ч
    reminder_sent_1h = Column(Integer, default=0)  # Отправлено напоминание за 1ч
    reminder_sent_10m = Column(Integer, default=0)  # Отправлено напоминание за 10м
    attended = Column(Integer, default=0)  # Посетил ли вебинар (0 - нет, 1 - да)