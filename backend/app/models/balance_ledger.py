from __future__ import annotations

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text, func

from app.database import Base


# Ledger types: deposit_request_created, deposit_request_approved, deposit_request_rejected, admin_adjust, withdrawal
class BalanceLedger(Base):
    __tablename__ = "balance_ledger"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    delta_cents = Column(BigInteger, nullable=False)
    balance_after_cents = Column(BigInteger, nullable=False)
    comment = Column(Text, nullable=True)
    ref_request_id = Column(Integer, ForeignKey("balance_requests.id", ondelete="SET NULL"), nullable=True)
    admin_id = Column(Integer, ForeignKey("admin_panel_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
