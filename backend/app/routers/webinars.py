from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.webinar import Webinar
from app.schemas.webinar import WebinarCreate, WebinarResponse

router = APIRouter(prefix="/webinars", tags=["webinars"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[WebinarResponse])
def get_webinars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    webinars = db.query(Webinar).offset(skip).limit(limit).all()
    return webinars


@router.get("/{webinar_id}", response_model=WebinarResponse)
def get_webinar(webinar_id: int, db: Session = Depends(get_db)):
    webinar = db.query(Webinar).filter(Webinar.id == webinar_id).first()
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    return webinar


@router.post("/", response_model=WebinarResponse)
def create_webinar(webinar: WebinarCreate, db: Session = Depends(get_db)):
    db_webinar = Webinar(**webinar.model_dump())
    db.add(db_webinar)
    db.commit()
    db.refresh(db_webinar)
    return db_webinar

