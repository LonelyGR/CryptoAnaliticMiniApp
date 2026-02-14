"""
Tests for balance: approve, adjust, double-approve prevention.
Run: pytest tests/test_balance.py -v
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
import app.models  # noqa: F401 - ensure all models registered
from app.models.balance_ledger import BalanceLedger
from app.models.balance_request import BalanceRequest
from app.models.user import User
from app.models.user_balance import UserBalance
from app.services.balance_service import (
    admin_adjust_balance,
    approve_deposit_request,
    get_balance_cents,
    reject_deposit_request,
)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def user(db):
    u = User(telegram_id=12345, username="test", first_name="Test")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def admin_user_id(db):
    """Mock admin_panel_users - we need an id for reviewed_by_admin_id."""
    from app.models.admin_panel_user import AdminPanelUser
    a = AdminPanelUser(username="admin_test", password_hash="x", role="admin")
    db.add(a)
    db.commit()
    db.refresh(a)
    return a.id


def test_approve_deposit_request(db, user, admin_user_id):
    req = BalanceRequest(user_id=user.id, tx_ref="0xabc123", status="pending")
    db.add(req)
    db.commit()
    db.refresh(req)

    approve_deposit_request(db, req.id, 10000, admin_user_id, "test approve")
    assert get_balance_cents(db, user.id) == 10000

    ledger = db.query(BalanceLedger).filter(BalanceLedger.ref_request_id == req.id).first()
    assert ledger is not None
    assert ledger.type == "deposit_request_approved"
    assert ledger.delta_cents == 10000
    assert ledger.balance_after_cents == 10000

    req2 = db.query(BalanceRequest).filter(BalanceRequest.id == req.id).first()
    assert req2.status == "approved"


def test_double_approve_rejected(db, user, admin_user_id):
    req = BalanceRequest(user_id=user.id, tx_ref="0xdef456", status="pending")
    db.add(req)
    db.commit()
    db.refresh(req)

    approve_deposit_request(db, req.id, 5000, admin_user_id)
    with pytest.raises(ValueError, match="status is approved"):
        approve_deposit_request(db, req.id, 3000, admin_user_id)

    assert get_balance_cents(db, user.id) == 5000  # Only first approve applied


def test_admin_adjust_balance(db, user, admin_user_id):
    ub = UserBalance(user_id=user.id, balance_cents=10000)
    db.add(ub)
    db.commit()

    admin_adjust_balance(db, user.id, 5000, admin_user_id, "bonus")
    assert get_balance_cents(db, user.id) == 15000

    admin_adjust_balance(db, user.id, -3000, admin_user_id, "refund")
    assert get_balance_cents(db, user.id) == 12000


def test_admin_adjust_balance_cannot_go_negative(db, user, admin_user_id):
    ub = UserBalance(user_id=user.id, balance_cents=1000)
    db.add(ub)
    db.commit()

    with pytest.raises(ValueError, match="cannot go below 0"):
        admin_adjust_balance(db, user.id, -2000, admin_user_id)


def test_reject_deposit_request(db, user, admin_user_id):
    req = BalanceRequest(user_id=user.id, tx_ref="0xreject", status="pending")
    db.add(req)
    db.commit()
    db.refresh(req)

    reject_deposit_request(db, req.id, admin_user_id, "invalid tx")
    req2 = db.query(BalanceRequest).filter(BalanceRequest.id == req.id).first()
    assert req2.status == "rejected"
    assert get_balance_cents(db, user.id) == 0


def test_double_reject_rejected(db, user, admin_user_id):
    req = BalanceRequest(user_id=user.id, tx_ref="0xdouble", status="pending")
    db.add(req)
    db.commit()
    db.refresh(req)

    reject_deposit_request(db, req.id, admin_user_id)
    with pytest.raises(ValueError, match="status is rejected"):
        reject_deposit_request(db, req.id, admin_user_id)
