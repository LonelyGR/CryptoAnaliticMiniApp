import os
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import SessionLocal
from app.models.user import User
from app.models.referral_invite import ReferralInvite
from app.schemas.referral import ReferralInfoResponse, ReferralInviteResponse, ReferralTrackRequest
from app.utils.telegram import send_telegram_message


router = APIRouter(prefix="/referrals", tags=["referrals"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_referral_code(db: Session) -> str:
    for _ in range(10):
        code = secrets.token_urlsafe(6).replace("-", "").replace("_", "")
        exists = db.query(User).filter(User.referral_code == code).first()
        if not exists:
            return code
    raise HTTPException(status_code=500, detail="Failed to generate referral code")


def build_referral_link(code: str) -> str:
    bot_username = (os.getenv("TELEGRAM_BOT_USERNAME") or "").strip()
    bot_username = bot_username.lstrip("@")
    if not bot_username:
        return ""
    return f"https://t.me/{bot_username}?start=ref_{code}"


@router.get("/{telegram_id}", response_model=ReferralInfoResponse)
def get_referral_info(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.referral_code:
        user.referral_code = generate_referral_code(db)
        db.commit()
        db.refresh(user)

    invites = (
        db.query(ReferralInvite)
        .filter(ReferralInvite.referrer_telegram_id == telegram_id)
        .order_by(desc(ReferralInvite.created_at))
        .all()
    )

    return {
        "referral_code": user.referral_code,
        "referral_link": build_referral_link(user.referral_code),
        "invited_count": len(invites),
        "invited": invites,
    }


@router.post("/track")
def track_referral_visit(payload: ReferralTrackRequest, db: Session = Depends(get_db)):
    referrer = db.query(User).filter(User.referral_code == payload.referral_code).first()
    if not referrer:
        raise HTTPException(status_code=404, detail="Referral code not found")

    if payload.referred_telegram_id and payload.referred_telegram_id == referrer.telegram_id:
        return {"created": False, "message": "Self referral ignored"}

    existing_invite = None
    if payload.referred_telegram_id:
        existing_invite = (
            db.query(ReferralInvite)
            .filter(
                ReferralInvite.referrer_telegram_id == referrer.telegram_id,
                ReferralInvite.referred_telegram_id == payload.referred_telegram_id,
            )
            .first()
        )

    if existing_invite:
        return {"created": False, "message": "Invite already exists"}

    referred_user = None
    if payload.referred_telegram_id:
        referred_user = db.query(User).filter(User.telegram_id == payload.referred_telegram_id).first()
        if referred_user and not referred_user.referred_by_telegram_id:
            referred_user.referred_by_telegram_id = referrer.telegram_id

    invite = ReferralInvite(
        referrer_telegram_id=referrer.telegram_id,
        referred_telegram_id=payload.referred_telegram_id,
        referred_username=payload.referred_username or (referred_user.username if referred_user else None),
        referred_first_name=payload.referred_first_name or (referred_user.first_name if referred_user else None),
        referred_last_name=payload.referred_last_name or (referred_user.last_name if referred_user else None),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    display_name = invite.referred_first_name or invite.referred_username or "Новый пользователь"
    message = (
        "✨ <b>Новый переход по вашей ссылке!</b>\n\n"
        f"👤 Пользователь: <b>{display_name}</b>\n"
        f"🆔 Telegram ID: <code>{invite.referred_telegram_id or 'не передан'}</code>\n\n"
        "Спасибо, что делитесь Crypto Sensey!"
    )
    send_telegram_message(referrer.telegram_id, message)

    return {"created": True, "invite_id": invite.id}
