from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.database import Base

class Webinar(Base):
    __tablename__ = "webinars"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)  # Дата в формате YYYY-MM-DD
    time = Column(String, nullable=False)  # Время в формате HH:MM
    duration = Column(String)  # Продолжительность, например "2 часа"
    speaker = Column(String)  # Имя спикера
    status = Column(String, default="upcoming")  # upcoming, completed, cancelled
    description = Column(Text)  # Описание вебинара
    price_usd = Column(Float, default=0.0)  # Цена вебинара в долларах
    price_eur = Column(Float, default=0.0)  # Цена вебинара в евро
    meeting_link = Column(String, nullable=True)  # Ссылка на видеовстречу
    meeting_platform = Column(String, nullable=True)  # Платформа (Zoom, Google Meet, Jitsi, YouTube, etc.)
    recording_link = Column(String, nullable=True)  # Ссылка на запись вебинара

