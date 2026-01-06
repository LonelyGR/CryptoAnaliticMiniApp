from sqlalchemy import Column, Integer, String, Text, DateTime
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

