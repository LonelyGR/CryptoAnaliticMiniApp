from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    webinar_id = Column(Integer, ForeignKey("webinars.id"), nullable=True)  # ID вебинара, если это запись на вебинар
    type = Column(String)  # webinar или consultation
    date = Column(String)  # Дата записи
    time = Column(String, nullable=True)  # Время для консультаций
    status = Column(String, default="active")  # active, confirmed, cancelled
    topic = Column(String, nullable=True)  # Тема для консультаций
    message = Column(String, nullable=True)  # Дополнительное сообщение