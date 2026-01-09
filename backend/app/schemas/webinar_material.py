from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WebinarMaterialBase(BaseModel):
    webinar_id: int
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None

class WebinarMaterialCreate(WebinarMaterialBase):
    pass

class WebinarMaterialResponse(WebinarMaterialBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
