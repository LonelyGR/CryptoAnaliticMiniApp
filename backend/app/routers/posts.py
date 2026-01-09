from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.post import Post
from app.models.admin import Admin
from app.schemas.post import PostCreate, PostResponse

router = APIRouter(prefix="/posts", tags=["posts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_admin_access(admin_telegram_id: int = Query(..., description="Telegram ID администратора"), db: Session = Depends(get_db)):
    """Проверка прав администратора для создания/редактирования постов"""
    admin = db.query(Admin).filter(Admin.telegram_id == admin_telegram_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора")
    # Проверяем, что роль - админ или разработчик
    if admin.role.lower() not in ['админ', 'администратор', 'разработчик', 'developer', 'admin']:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора или разработчика")
    return admin


@router.get("/", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех постов (доступно всем)"""
    posts = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Получить пост по ID (доступно всем)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=PostResponse)
def create_post(
    post: PostCreate,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Создать пост (только для администраторов и разработчиков)"""
    check_admin_access(admin_telegram_id, db)
    
    db_post = Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post: PostCreate,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Обновить пост (только для администраторов и разработчиков)"""
    check_admin_access(admin_telegram_id, db)
    
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    for key, value in post.model_dump().items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Удалить пост (только для администраторов и разработчиков)"""
    check_admin_access(admin_telegram_id, db)
    
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}
