"""
Manual tests for balance: approve, adjust, double-approve prevention.
Run: python test_balance_manual.py
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
import app.models  # noqa: F401
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


def run_tests():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Create admin user
    from app.models.admin_panel_user import AdminPanelUser
    a = AdminPanelUser(username="admin_test", password_hash="x", role="admin")
    db.add(a)
    db.commit()
    db.refresh(a)
    admin_id = a.id

    # Create app user
    u = User(telegram_id=12345, username="test", first_name="Test")
    db.add(u)
    db.commit()
    db.refresh(u)

    ok = 0
    fail = 0

    # 1. Approve deposit
    req = BalanceRequest(user_id=u.id, tx_ref="0xabc", status="pending")
    db.add(req)
    db.commit()
    db.refresh(req)
    approve_deposit_request(db, req.id, 10000, admin_id)
    assert get_balance_cents(db, u.id) == 10000
    print("OK: approve_deposit_request")
    ok += 1

    # 2. Double approve rejected
    req2 = BalanceRequest(user_id=u.id, tx_ref="0xdef", status="pending")
    db.add(req2)
    db.commit()
    db.refresh(req2)
    approve_deposit_request(db, req2.id, 5000, admin_id)
    try:
        approve_deposit_request(db, req2.id, 3000, admin_id)
        print("FAIL: double approve should have raised")
        fail += 1
    except ValueError as e:
        if "status is approved" in str(e):
            print("OK: double approve rejected")
            ok += 1
        else:
            print(f"FAIL: wrong error {e}")
            fail += 1
    assert get_balance_cents(db, u.id) == 15000  # 10k + 5k only

    # 3. Admin adjust
    admin_adjust_balance(db, u.id, -2000, admin_id, "refund")
    assert get_balance_cents(db, u.id) == 13000
    print("OK: admin_adjust_balance")
    ok += 1

    # 4. Cannot go negative
    try:
        admin_adjust_balance(db, u.id, -20000, admin_id)
        print("FAIL: negative balance should have raised")
        fail += 1
    except ValueError as e:
        if "cannot go below 0" in str(e):
            print("OK: negative balance rejected")
            ok += 1
        else:
            print(f"FAIL: wrong error {e}")
            fail += 1

    db.close()
    print(f"\nResult: {ok} passed, {fail} failed")
    return fail == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
