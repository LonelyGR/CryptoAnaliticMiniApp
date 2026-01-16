from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ReferralInviteResponse(BaseModel):
    id: int
    referred_telegram_id: Optional[int] = None
    referred_username: Optional[str] = None
    referred_first_name: Optional[str] = None
    referred_last_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralInfoResponse(BaseModel):
    referral_code: str
    referral_link: Optional[str] = None
    invited_count: int
    invited: List[ReferralInviteResponse]


class ReferralTrackRequest(BaseModel):
    referral_code: str
    referred_telegram_id: Optional[int] = None
    referred_username: Optional[str] = None
    referred_first_name: Optional[str] = None
    referred_last_name: Optional[str] = None
