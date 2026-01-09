from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.webinar_material import WebinarMaterial
from app.models.webinar import Webinar
from app.models.admin import Admin
from app.schemas.webinar_material import WebinarMaterialCreate, WebinarMaterialResponse

router = APIRouter(prefix="/webinar-materials", tags=["webinar-materials"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_admin_access(admin_telegram_id: int = Query(..., description="Telegram ID администратора"), db: Session = Depends(get_db)):
    """Проверка прав администратора"""
    admin = db.query(Admin).filter(Admin.telegram_id == admin_telegram_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора")
    return admin


@router.get("/webinar/{webinar_id}", response_model=List[WebinarMaterialResponse])
def get_webinar_materials(webinar_id: int, db: Session = Depends(get_db)):
    """Получить все материалы вебинара (доступно всем)"""
    materials = db.query(WebinarMaterial).filter(WebinarMaterial.webinar_id == webinar_id).all()
    return materials


@router.post("/", response_model=WebinarMaterialResponse)
def create_webinar_material(
    material: WebinarMaterialCreate,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Создать материал для вебинара (только для администраторов)"""
    check_admin_access(admin_telegram_id, db)
    
    # Проверяем, что вебинар существует
    webinar = db.query(Webinar).filter(Webinar.id == material.webinar_id).first()
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    
    db_material = WebinarMaterial(**material.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


@router.put("/{material_id}", response_model=WebinarMaterialResponse)
def update_webinar_material(
    material_id: int,
    material: WebinarMaterialCreate,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Обновить материал вебинара (только для администраторов)"""
    check_admin_access(admin_telegram_id, db)
    
    db_material = db.query(WebinarMaterial).filter(WebinarMaterial.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    for key, value in material.model_dump().items():
        setattr(db_material, key, value)
    
    db.commit()
    db.refresh(db_material)
    return db_material


@router.delete("/{material_id}")
def delete_webinar_material(
    material_id: int,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Удалить материал вебинара (только для администраторов)"""
    check_admin_access(admin_telegram_id, db)
    
    db_material = db.query(WebinarMaterial).filter(WebinarMaterial.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    db.delete(db_material)
    db.commit()
    return {"message": "Material deleted successfully"}
