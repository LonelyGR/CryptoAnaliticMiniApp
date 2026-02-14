"""
/me endpoints: require Telegram WebApp auth. Resolves user by initData.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.schemas.balance import (
    BalanceRequestCreate,
    BalanceRequestResponse,
    BalanceResponse,
    DepositAddressResponse,
)
from app.services.balance_service import (
    CURRENCY,
    _format_money,
    create_deposit_request,
    get_balance_cents,
    get_or_create_balance,
)
from app.utils.telegram_webapp import get_request_telegram_user_id

router = APIRouter(prefix="/me", tags=["me"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _resolve_user(request: Request, db: Session) -> User:
    telegram_id = get_request_telegram_user_id(request)
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="User is blocked")
    return user


@router.get("/balance", response_model=BalanceResponse)
def get_my_balance(
    request: Request,
    db: Session = Depends(get_db),
):
    """Get current user balance."""
    user = _resolve_user(request, db)
    cents = get_balance_cents(db, user.id)
    return BalanceResponse(
        balance_cents=cents,
        balance_formatted=_format_money(cents),
        currency=CURRENCY,
    )


@router.get("/deposit-address", response_model=DepositAddressResponse)
def get_deposit_address(
    request: Request,
    db: Session = Depends(get_db),
):
    """Get static deposit address for crypto payments."""
    _resolve_user(request, db)  # auth check
    import os

    address = (os.getenv("DEPOSIT_ADDRESS") or "").strip() or "TBD_SET_DEPOSIT_ADDRESS"
    network = (os.getenv("DEPOSIT_NETWORK") or "USDT TRC20").strip()
    return DepositAddressResponse(
        address=address,
        network_label=network,
        qr_payload=address,
    )


@router.post("/balance-requests", response_model=BalanceRequestResponse)
def create_balance_request(
    request: Request,
    body: BalanceRequestCreate,
    db: Session = Depends(get_db),
):
    """Submit deposit request with tx hash/explorer url."""
    user = _resolve_user(request, db)
    req = create_deposit_request(db, user.id, body.tx_ref)
    return BalanceRequestResponse(id=req.id, status=req.status)


@router.get("/balance-requests")
def get_my_balance_requests(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    """Optional: list user's own deposit requests."""
    user = _resolve_user(request, db)
    from app.models.balance_request import BalanceRequest

    offset = (page - 1) * limit
    total = db.query(BalanceRequest).filter(BalanceRequest.user_id == user.id).count()
    items = (
        db.query(BalanceRequest)
        .filter(BalanceRequest.user_id == user.id)
        .order_by(BalanceRequest.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    pages = (total + limit - 1) // limit if limit else 0
    return {
        "items": [
            {
                "id": r.id,
                "tx_ref": r.tx_ref,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in items
        ],
        "page": page,
        "pages": pages,
        "total": total,
    }
