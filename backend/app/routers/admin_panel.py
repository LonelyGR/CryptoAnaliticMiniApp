import os
import secrets

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.templating import Jinja2Templates

from app.database import SessionLocal
from app.database import Base
from app.models.post import Post
from app.models.webinar import Webinar
from app.models.booking import Booking
from app.models.admin import Admin
from app.models.user import User

# Reuse DB-clear helpers (works for sqlite + postgres)
from app.routers.admins import _clear_all_tables, _clear_selected_tables  # noqa: F401

router = APIRouter(prefix="/admin", tags=["admin-panel"])
security = HTTPBasic()

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "admin_templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_basic_auth(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    username = (os.getenv("ADMIN_PANEL_USERNAME") or "").strip()
    password = (os.getenv("ADMIN_PANEL_PASSWORD") or "").strip()
    if not username or not password:
        raise HTTPException(status_code=503, detail="ADMIN_PANEL_USERNAME / ADMIN_PANEL_PASSWORD are not configured")

    is_user_ok = secrets.compare_digest(credentials.username or "", username)
    is_pass_ok = secrets.compare_digest(credentials.password or "", password)
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(status_code=401, detail="Invalid credentials")


def _render(request: Request, name: str, *, section: str, title: str, **ctx):
    # simple flash via query params
    flash = request.query_params.get("flash")
    flash_kind = request.query_params.get("kind")  # ok|bad
    flash_details = request.query_params.get("details")
    return templates.TemplateResponse(
        name,
        {
            "request": request,
            "section": section,
            "title": title,
            "flash": flash,
            "flash_kind": flash_kind,
            "flash_details": flash_details,
            **ctx,
        },
    )


def _redir(url: str, *, flash: str | None = None, kind: str = "ok", details: str | None = None) -> RedirectResponse:
    if flash:
        from urllib.parse import urlencode

        q = {"flash": flash, "kind": kind}
        if details:
            q["details"] = details
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{urlencode(q)}"
    return RedirectResponse(url=url, status_code=303)


@router.get("/")
def admin_root(_: None = Depends(require_basic_auth)):
    return _redir("/admin/posts")


@router.get("/posts")
def admin_posts(request: Request, _: None = Depends(require_basic_auth), db=Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(200).all()
    return _render(request, "posts.html", section="posts", title="Admin · Посты", posts=posts)


@router.post("/posts/create")
def admin_posts_create(
    _: None = Depends(require_basic_auth),
    db=Depends(get_db),
    title: str = Form(...),
    content: str = Form(...),
):
    p = Post(title=title.strip(), content=content.strip())
    db.add(p)
    db.commit()
    return _redir("/admin/posts", flash="Пост создан", kind="ok")


@router.post("/posts/{post_id}/delete")
def admin_posts_delete(post_id: int, _: None = Depends(require_basic_auth), db=Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        return _redir("/admin/posts", flash="Пост не найден", kind="bad")
    db.delete(p)
    db.commit()
    return _redir("/admin/posts", flash=f"Пост {post_id} удалён", kind="ok")


@router.get("/webinars")
def admin_webinars(request: Request, _: None = Depends(require_basic_auth), db=Depends(get_db)):
    webinars = db.query(Webinar).order_by(Webinar.id.desc()).limit(200).all()
    return _render(request, "webinars.html", section="webinars", title="Admin · Вебинары", webinars=webinars)


@router.post("/webinars/create")
def admin_webinars_create(
    _: None = Depends(require_basic_auth),
    db=Depends(get_db),
    title: str = Form(...),
    date_: str = Form(..., alias="date"),
    time: str = Form(...),
    duration: str = Form(""),
    speaker: str = Form(""),
    status: str = Form("upcoming"),
    description: str = Form(""),
    price_usd: float = Form(0.0),
    meeting_link: str = Form(""),
):
    # date stored as string in schema/model? keep as provided
    w = Webinar(
        title=title.strip(),
        date=date_.strip(),
        time=time.strip(),
        duration=(duration or "").strip(),
        speaker=(speaker or "").strip(),
        status=(status or "upcoming").strip(),
        description=(description or "").strip(),
        price_usd=float(price_usd or 0.0),
        price_eur=0.0,
        meeting_link=(meeting_link or "").strip() or None,
        meeting_platform=None,
        recording_link=None,
    )
    db.add(w)
    db.commit()
    return _redir("/admin/webinars", flash="Вебинар создан", kind="ok")


@router.post("/webinars/{webinar_id}/delete")
def admin_webinars_delete(webinar_id: int, _: None = Depends(require_basic_auth), db=Depends(get_db)):
    w = db.query(Webinar).filter(Webinar.id == webinar_id).first()
    if not w:
        return _redir("/admin/webinars", flash="Вебинар не найден", kind="bad")
    db.delete(w)
    db.commit()
    return _redir("/admin/webinars", flash=f"Вебинар {webinar_id} удалён", kind="ok")


@router.get("/tickets")
def admin_tickets(request: Request, _: None = Depends(require_basic_auth), db=Depends(get_db)):
    support = (
        db.query(Booking)
        .filter(Booking.type == "support")
        .order_by(Booking.id.desc())
        .limit(200)
        .all()
    )
    consultations = (
        db.query(Booking)
        .filter(Booking.type == "consultation")
        .order_by(Booking.id.desc())
        .limit(200)
        .all()
    )

    # enrich minimal fields (same as API does)
    def to_admin_dict(b: Booking):
        u = db.query(User).filter(User.id == b.user_id).first()
        return {
            "id": b.id,
            "type": b.type,
            "status": b.status,
            "topic": b.topic,
            "message": b.message,
            "admin_response": b.admin_response,
            "user_telegram_id": getattr(u, "telegram_id", None) if u else None,
            "user_first_name": getattr(u, "first_name", None) if u else None,
            "user_username": getattr(u, "username", None) if u else None,
        }

    support_ctx = [to_admin_dict(x) for x in support]
    consult_ctx = [to_admin_dict(x) for x in consultations]
    return _render(
        request,
        "tickets.html",
        section="tickets",
        title="Admin · Тикеты",
        support=support_ctx,
        consultations=consult_ctx,
    )


@router.post("/tickets/{ticket_id}/respond")
def admin_ticket_respond(
    ticket_id: int,
    _: None = Depends(require_basic_auth),
    db=Depends(get_db),
    admin_response: str = Form(...),
):
    b = db.query(Booking).filter(Booking.id == ticket_id).first()
    if not b:
        return _redir("/admin/tickets", flash="Тикет не найден", kind="bad")
    b.admin_response = admin_response.strip()
    # Set a sane status if exists
    if (b.status or "").lower() in ("pending", "active", "new", ""):
        b.status = "answered"
    db.commit()
    return _redir("/admin/tickets", flash=f"Ответ сохранён (тикет {ticket_id})", kind="ok")


@router.get("/admins")
def admin_admins(request: Request, _: None = Depends(require_basic_auth), db=Depends(get_db)):
    admins = db.query(Admin).order_by(Admin.id.asc()).all()
    return _render(request, "admins.html", section="admins", title="Admin · Админы", admins=admins)


@router.post("/admins/create")
def admin_admins_create(
    _: None = Depends(require_basic_auth),
    db=Depends(get_db),
    telegram_id: int = Form(...),
    role: str = Form("Администратор"),
):
    exists = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if exists:
        exists.role = role
        db.commit()
        return _redir("/admin/admins", flash="Админ обновлён (уже существовал)", kind="ok")
    a = Admin(telegram_id=telegram_id, role=role)
    db.add(a)
    db.commit()
    return _redir("/admin/admins", flash="Админ добавлен", kind="ok")


@router.post("/admins/{admin_id}/update")
def admin_admins_update(
    admin_id: int,
    _: None = Depends(require_basic_auth),
    db=Depends(get_db),
    role: str = Form(...),
):
    a = db.query(Admin).filter(Admin.id == admin_id).first()
    if not a:
        return _redir("/admin/admins", flash="Админ не найден", kind="bad")
    a.role = role
    db.commit()
    return _redir("/admin/admins", flash="Роль обновлена", kind="ok")


@router.post("/admins/{admin_id}/delete")
def admin_admins_delete(admin_id: int, _: None = Depends(require_basic_auth), db=Depends(get_db)):
    a = db.query(Admin).filter(Admin.id == admin_id).first()
    if not a:
        return _redir("/admin/admins", flash="Админ не найден", kind="bad")
    db.delete(a)
    db.commit()
    return _redir("/admin/admins", flash="Админ удалён", kind="ok")


@router.get("/data")
def admin_data(request: Request, _: None = Depends(require_basic_auth), db=Depends(get_db)):
    tables = [t.name for t in Base.metadata.sorted_tables]
    return _render(request, "data.html", section="data", title="Admin · Данные", tables=tables)


@router.post("/data/clear-db")
def admin_clear_db(_: None = Depends(require_basic_auth), db=Depends(get_db)):
    deleted = _clear_all_tables(db)
    db.commit()
    return _redir("/admin/data", flash="База очищена", kind="ok", details=f"deleted_rows={deleted}")


@router.post("/data/clear-selected")
def admin_clear_selected(
    _: None = Depends(require_basic_auth),
    db=Depends(get_db),
    targets: list[str] = Form(...),
):
    targets_set = {t.strip() for t in (targets or []) if t and t.strip()}
    deleted, details = _clear_selected_tables(db, targets_set)
    db.commit()
    return _redir("/admin/data", flash="Выбранные данные удалены", kind="ok", details=f"deleted_rows={deleted}")

