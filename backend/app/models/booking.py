from sqlalchemy import Column, Integer, String
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    type = Column(String)
    date = Column(String)
    status = Column(String, default="active")