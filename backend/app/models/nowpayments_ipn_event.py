from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class NowPaymentsIpnEvent(Base):
    __tablename__ = "nowpayments_ipn_events"

    id = Column(Integer, primary_key=True)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

    payment_id = Column(String, nullable=True, index=True)
    payment_status = Column(String, nullable=True, index=True)
    order_id = Column(String, nullable=True, index=True)

    signature_valid = Column(Boolean, nullable=False, default=False)
    signature_header = Column(String, nullable=True)

    payload_json = Column(Text, nullable=True)

