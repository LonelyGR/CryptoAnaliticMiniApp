from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class WebinarMaterial(Base):
    __tablename__ = "webinar_materials"

    id = Column(Integer, primary_key=True)
    webinar_id = Column(Integer, ForeignKey("webinars.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String, nullable=True)  # Ссылка на файл
    file_type = Column(String, nullable=True)  # pdf, video, link, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
