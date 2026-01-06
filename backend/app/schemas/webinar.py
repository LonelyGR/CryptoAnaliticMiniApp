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

class WebinarCreate(WebinarBase):
    pass

class WebinarResponse(WebinarBase):
    id: int

    class Config:
        from_attributes = True

