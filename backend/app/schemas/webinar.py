from pydantic import BaseModel
from typing import Optional

class WebinarBase(BaseModel):
    title: str
    date: str
    time: str
    duration: Optional[str] = None
    speaker: Optional[str] = None
    status: str = "upcoming"
    description: Optional[str] = None
    price_usd: Optional[float] = 0.0
    price_eur: Optional[float] = 0.0
    meeting_link: Optional[str] = None
    meeting_platform: Optional[str] = None
    recording_link: Optional[str] = None

class WebinarCreate(WebinarBase):
    pass

class WebinarResponse(WebinarBase):
    id: int

    class Config:
        from_attributes = True

