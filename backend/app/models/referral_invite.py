from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class ReferralInvite(Base):
    __tablename__ = "referral_invites"

    id = Column(Integer, primary_key=True)
    referrer_telegram_id = Column(Integer, index=True, nullable=False)
    referred_telegram_id = Column(Integer, index=True, nullable=True)
    referred_username = Column(String, nullable=True)
    referred_first_name = Column(String, nullable=True)
    referred_last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
