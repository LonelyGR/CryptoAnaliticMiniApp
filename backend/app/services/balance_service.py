"""
Balance service: balance operations, deposit requests, ledger.
All balance changes must be transactional and recorded in ledger.
"""
from __future__ import annotations

import decimal
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.balance_ledger import BalanceLedger
from app.models.balance_request import BalanceRequest
from app.models.user import User
from app.models.user_balance import UserBalance

logger = logging.getLogger("app")

CURRENCY = (os.getenv("CURRENCY") or "KZT").strip().upper()


def _format_money(cents: int, currency: str = CURRENCY) -> str:
    """Format cents as human-readable money string."""
    amount = decimal.Decimal(cents) / 100
    return f"{amount:,.2f} {currency}"


def parse_money(value: str | float | int) -> int:
    """Parse human input to cents. Accepts '12.50', 12.5, 1250."""
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value * 100))
    s = str(value).strip().replace(",", ".").replace(" ", "")
    if not s:
        return 0
    try:
        d = decimal.Decimal(s)
        return int((d * 100).quantize(decimal.Decimal("1")))
    except Exception:
        raise ValueError(f"Invalid money format: {value!r}")


def get_or_create_balance(db: Session, user_id: int) -> UserBalance:
    """Get user balance or create with 0."""
    ub = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
    if not ub:
        ub = UserBalance(user_id=user_id, balance_cents=0)
        db.add(ub)
        db.commit()
        db.refresh(ub)
    return ub


def get_balance_cents(db: Session, user_id: int) -> int:
    ub = get_or_create_balance(db, user_id)
    return int(ub.balance_cents or 0)


def create_deposit_request(db: Session, user_id: int, tx_ref: str) -> BalanceRequest:
    """Create deposit request with status pending. Optionally add ledger entry."""
    req = BalanceRequest(
        user_id=user_id,
        tx_ref=tx_ref.strip(),
        status="pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    # Optional ledger: deposit_request_created, delta=0
    _append_ledger(
        db,
        user_id=user_id,
        type_="deposit_request_created",
        delta_cents=0,
        balance_after=get_balance_cents(db, user_id),
        ref_request_id=req.id,
    )
    return req


def approve_deposit_request(
    db: Session,
    request_id: int,
    amount_cents: int,
    admin_id: int,
    comment: Optional[str] = None,
) -> BalanceRequest:
    """
    Approve deposit request: update status, add to balance, ledger.
    Must be called within transaction. Raises if already processed.
    """
    req = db.query(BalanceRequest).filter(BalanceRequest.id == request_id).first()
    if not req:
        raise ValueError("Balance request not found")
    if req.status != "pending":
        raise ValueError(f"Cannot approve: request status is {req.status}")

    ub = get_or_create_balance(db, req.user_id)
    new_balance = int(ub.balance_cents or 0) + amount_cents
    ub.balance_cents = new_balance
    req.status = "approved"
    req.reviewed_at = datetime.now(timezone.utc)
    req.reviewed_by_admin_id = admin_id
    req.admin_comment = comment

    _append_ledger(
        db,
        user_id=req.user_id,
        type_="deposit_request_approved",
        delta_cents=amount_cents,
        balance_after=new_balance,
        comment=comment,
        ref_request_id=req.id,
        admin_id=admin_id,
    )
    db.commit()
    db.refresh(req)
    return req


def reject_deposit_request(
    db: Session,
    request_id: int,
    admin_id: int,
    comment: Optional[str] = None,
) -> BalanceRequest:
    """Reject deposit request. Must be called within transaction."""
    req = db.query(BalanceRequest).filter(BalanceRequest.id == request_id).first()
    if not req:
        raise ValueError("Balance request not found")
    if req.status != "pending":
        raise ValueError(f"Cannot reject: request status is {req.status}")

    req.status = "rejected"
    req.reviewed_at = datetime.now(timezone.utc)
    req.reviewed_by_admin_id = admin_id
    req.admin_comment = comment

    balance = get_balance_cents(db, req.user_id)
    _append_ledger(
        db,
        user_id=req.user_id,
        type_="deposit_request_rejected",
        delta_cents=0,
        balance_after=balance,
        comment=comment,
        ref_request_id=req.id,
        admin_id=admin_id,
    )
    db.commit()
    db.refresh(req)
    return req


def admin_adjust_balance(
    db: Session,
    user_id: int,
    delta_cents: int,
    admin_id: int,
    comment: Optional[str] = None,
    allow_negative: bool = False,
) -> UserBalance:
    """
    Admin adjust user balance. By default, balance cannot go below 0.
    """
    ub = get_or_create_balance(db, user_id)
    current = int(ub.balance_cents or 0)
    new_balance = current + delta_cents
    if not allow_negative and new_balance < 0:
        raise ValueError(f"Balance cannot go below 0. Current: {current}, delta: {delta_cents}")
    ub.balance_cents = new_balance
    _append_ledger(
        db,
        user_id=user_id,
        type_="admin_adjust",
        delta_cents=delta_cents,
        balance_after=new_balance,
        comment=comment,
        admin_id=admin_id,
    )
    db.commit()
    db.refresh(ub)
    return ub


def _append_ledger(
    db: Session,
    *,
    user_id: int,
    type_: str,
    delta_cents: int,
    balance_after: int,
    comment: Optional[str] = None,
    ref_request_id: Optional[int] = None,
    admin_id: Optional[int] = None,
) -> None:
    entry = BalanceLedger(
        user_id=user_id,
        type=type_,
        delta_cents=delta_cents,
        balance_after_cents=balance_after,
        comment=comment,
        ref_request_id=ref_request_id,
        admin_id=admin_id,
    )
    db.add(entry)
