import os
import secrets
import hmac
import hashlib
import time
import base64

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from urllib.parse import urlencode

from app.database import SessionLocal
from app.database import Base
from app.models.post import Post
from app.models.webinar import Webinar
from app.models.booking import Booking
from app.models.admin import Admin
from app.models.user import User
from app.models.payment import Payment
from app.models.referral_invite import ReferralInvite
from app.models.admin_panel_user import AdminPanelUser
from app.models.balance_request import BalanceRequest
from app.models.balance_ledger import BalanceLedger
from app.models.user_balance import UserBalance
from app.services.balance_service import (
    _format_money,
    admin_adjust_balance,
    approve_deposit_request,
    get_balance_cents,
    get_or_create_balance,
    parse_money,
    reject_deposit_request,
)

# Reuse DB-clear helpers (works for sqlite + postgres)
from app.routers.admins import _clear_all_tables, _clear_selected_tables  # noqa: F401

router = APIRouter(prefix="/admin", tags=["admin-panel"])

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "admin_templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _admin_secret() -> str:
    secret = (os.getenv("ADMIN_PANEL_SECRET") or "").strip()
    if not secret:
        raise HTTPException(status_code=503, detail="ADMIN_PANEL_SECRET is not configured")
    return secret


def _session_ttl_seconds() -> int:
    try:
        return int(os.getenv("ADMIN_PANEL_SESSION_TTL_SECONDS") or "604800")  # 7 days
    except Exception:
        return 604800


def _sign(secret: str, payload: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

def _pbkdf2_hash_password(password: str) -> str:
    # Format: pbkdf2_sha256$iterations$salt_b64$hash_b64
    iterations = int(os.getenv("ADMIN_PANEL_PBKDF2_ITERS") or "200000")
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
    return "pbkdf2_sha256$%d$%s$%s" % (
        iterations,
        base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
        base64.urlsafe_b64encode(dk).decode("ascii").rstrip("="),
    )


def _pbkdf2_verify(password: str, encoded: str) -> bool:
    try:
        algo, iters_s, salt_b64, hash_b64 = encoded.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iters_s)
        pad = "=" * (-len(salt_b64) % 4)
        salt = base64.urlsafe_b64decode((salt_b64 + pad).encode("ascii"))
        pad2 = "=" * (-len(hash_b64) % 4)
        expected = base64.urlsafe_b64decode((hash_b64 + pad2).encode("ascii"))
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=len(expected))
        return secrets.compare_digest(dk, expected)
    except Exception:
        return False


def _normalize_scopes(raw: str | None) -> str | None:
    if raw is None:
        return None
    s = raw.strip()
    if not s:
        return None
    # normalize comma-separated
    parts = []
    for p in s.split(","):
        p = p.strip().lower()
        if not p:
            continue
        parts.append(p)
    return ",".join(dict.fromkeys(parts))  # stable unique


def _role_default_scopes(role: str) -> set[str]:
    r = (role or "").strip().lower()
    if r in ("developer", "разработчик", "owner", "владелец"):
        return {"*"}
    if r in ("admin", "админ", "администратор"):
        return {
            "posts:view", "posts:write", "posts:delete",
            "webinars:view", "webinars:write", "webinars:delete",
            "tickets:view", "tickets:respond",
            "data:view", "data:delete",
            "admins:manage",
            "balance:view", "balance:manage",
        }
    if r in ("support", "поддержка"):
        return {"tickets:view", "tickets:respond"}
    if r in ("editor", "редактор"):
        return {"posts:view", "posts:write", "webinars:view", "webinars:write"}
    # Unknown roles: no access by default (explicit scopes recommended)
    return set()


def _user_scopes(u: AdminPanelUser) -> set[str]:
    if u.scopes:
        return {p.strip().lower() for p in u.scopes.split(",") if p.strip()}
    return _role_default_scopes(u.role)


def _has_scope(u: AdminPanelUser, scope: str) -> bool:
    scopes = _user_scopes(u)
    if "*" in scopes:
        return True
    s = scope.strip().lower()
    if s in scopes:
        return True
    # Backward-compatible aliases (old coarse scopes)
    coarse = s.split(":", 1)[0]
    if coarse in scopes:
        return True
    # Wildcards like "posts:*"
    if ":" in s:
        prefix = s.split(":", 1)[0]
        if f"{prefix}:*" in scopes:
            return True
    return False


ADMIN_PERMS: list[tuple[str, str, str, str]] = [
    # (group, scope, title, description)
    ("Посты", "posts:view", "Просмотр постов", "Видеть список постов в панели"),
    ("Посты", "posts:write", "Создание/редактирование постов", "Создавать новые посты"),
    ("Посты", "posts:delete", "Удаление постов", "Удалять посты"),

    ("Вебинары", "webinars:view", "Просмотр вебинаров", "Видеть список вебинаров"),
    ("Вебинары", "webinars:write", "Создание/редактирование вебинаров", "Создавать вебинары"),
    ("Вебинары", "webinars:delete", "Удаление вебинаров", "Удалять вебинары"),

    ("Тикеты", "tickets:view", "Просмотр тикетов", "Видеть обращения (support/consultation)"),
    ("Тикеты", "tickets:respond", "Ответы на тикеты", "Отвечать пользователям"),

    ("Данные", "data:view", "Просмотр данных", "Счётчики и последние записи в разделе Данные"),
    ("Данные", "data:delete", "Удаление данных", "Удалять данные (всё или выборочно)"),

    ("Управление", "admins:manage", "Управление Telegram-админами", "Добавлять/удалять админов приложения"),
    ("Управление", "users:manage", "Управление пользователями панели", "Создавать аккаунты/роли/права для панели"),

    ("Баланс", "balance:view", "Просмотр заявок и балансов", "Видеть заявки на пополнение и балансы пользователей"),
    ("Баланс", "balance:manage", "Управление балансом", "Подтверждать/отклонять заявки, изменять баланс"),
]


def _perms_to_scopes(perms: list[str] | None) -> str | None:
    if not perms:
        return None
    perms_norm = []
    for p in perms:
        p = (p or "").strip().lower()
        if not p:
            continue
        perms_norm.append(p)
    if "*" in perms_norm:
        return "*"
    return _normalize_scopes(",".join(perms_norm))


def _ensure_bootstrap_user(db) -> None:
    """
    Creates first admin panel user from env if table is empty.
    Env priority:
    - ADMIN_PANEL_BOOTSTRAP_USERNAME / ADMIN_PANEL_BOOTSTRAP_PASSWORD / ADMIN_PANEL_BOOTSTRAP_ROLE
    - fallback: ADMIN_PANEL_USERNAME / ADMIN_PANEL_PASSWORD / ADMIN_PANEL_ROLE
    """
    if db.query(AdminPanelUser).count() > 0:
        return

    u = (os.getenv("ADMIN_PANEL_BOOTSTRAP_USERNAME") or os.getenv("ADMIN_PANEL_USERNAME") or "").strip()
    p = (os.getenv("ADMIN_PANEL_BOOTSTRAP_PASSWORD") or os.getenv("ADMIN_PANEL_PASSWORD") or "").strip()
    role = (os.getenv("ADMIN_PANEL_BOOTSTRAP_ROLE") or os.getenv("ADMIN_PANEL_ROLE") or "developer").strip()
    if not u or not p:
        # no bootstrap configured; allow panel to start but login will show error
        return

    _admin_secret()  # ensure configured
    user = AdminPanelUser(
        username=u,
        password_hash=_pbkdf2_hash_password(p),
        role=role,
        scopes="*",
        is_active=True,
        session_version=0,
    )
    db.add(user)
    db.commit()


def _make_session_token(user_id: int, session_version: int) -> str:
    secret = _admin_secret()
    ts = str(int(time.time()))
    payload = f"v2|{user_id}|{session_version}|{ts}"
    sig = _sign(secret, payload)
    return f"{payload}|{sig}"


def _verify_session_token(token: str) -> tuple[int, int] | None:
    secret = (os.getenv("ADMIN_PANEL_SECRET") or "").strip()
    if not secret:
        return None
    token = (token or "").strip()
    parts = token.split("|")
    if len(parts) != 5:
        return None
    v, user_id_s, ver_s, ts, sig = parts
    if v != "v2":
        return None
    if not user_id_s.isdigit() or not ver_s.isdigit():
        return None
    if not ts.isdigit():
        return None
    payload = f"{v}|{user_id_s}|{ver_s}|{ts}"
    expected = _sign(secret, payload)
    if not secrets.compare_digest(expected, sig):
        return None
    age = int(time.time()) - int(ts)
    if age < 0:
        return None
    if _session_ttl_seconds() > 0 and age > _session_ttl_seconds():
        return None
    return int(user_id_s), int(ver_s)

def _login_location(*, next_url: str | None = None, flash: str | None = None, kind: str | None = None) -> str:
    """
    Build ASCII-safe Location header to /admin/login.
    IMPORTANT: headers must be latin-1/ASCII, so we always percent-encode query params.
    """
    q: dict[str, str] = {}
    if next_url:
        q["next"] = next_url
    if flash:
        q["flash"] = flash
    if kind:
        q["kind"] = kind
    if not q:
        return "/admin/login"
    return "/admin/login?" + urlencode(q, encoding="utf-8", errors="strict")


def require_admin_session(request: Request, db=Depends(get_db)) -> AdminPanelUser:
    _ensure_bootstrap_user(db)
    token_data = _verify_session_token(request.cookies.get("admin_session") or "")
    if not token_data:
        # redirect to login with next
        next_url = request.url.path
        if request.url.query:
            next_url = f"{next_url}?{request.url.query}"
        raise HTTPException(status_code=303, headers={"Location": _login_location(next_url=next_url)})
    user_id, ver = token_data
    u = db.query(AdminPanelUser).filter(AdminPanelUser.id == user_id).first()
    if not u or not u.is_active:
        raise HTTPException(status_code=303, headers={"Location": _login_location(flash="Сессия недействительна", kind="bad")})
    if int(u.session_version or 0) != int(ver):
        raise HTTPException(status_code=303, headers={"Location": _login_location(flash="Сессия устарела", kind="bad")})
    return u


def require_scope(scope: str):
    def _dep(user: AdminPanelUser = Depends(require_admin_session)) -> AdminPanelUser:
        if not _has_scope(user, scope):
            # Friendly forbidden page (keep navbar)
            raise HTTPException(status_code=303, headers={"Location": f"/admin/forbidden?need={scope}"})
        return user
    return _dep


@router.get("/forbidden")
def admin_forbidden(
    request: Request,
    user: AdminPanelUser = Depends(require_admin_session),
):
    need = request.query_params.get("need") or ""
    return _render(
        request,
        "forbidden.html",
        section="",
        title="Admin · Доступ запрещён",
        need=need,
        admin_user=f"{user.username} · {user.role}",
        can_manage_users=_has_scope(user, "users:manage"),
    )


@router.get("/ping")
def admin_ping():
    # No auth on purpose: helps diagnose routing (/admin should reach backend, not React)
    return {"ok": True, "service": "admin-panel"}


def _render(request: Request, name: str, *, section: str, title: str, **ctx):
    # simple flash via query params
    flash = request.query_params.get("flash")
    flash_kind = request.query_params.get("kind")  # ok|bad
    flash_details = request.query_params.get("details")
    static_v = (os.getenv("ADMIN_STATIC_VERSION") or "").strip() or "dev"
    return templates.TemplateResponse(
        name,
        {
            "request": request,
            "section": section,
            "title": title,
            "admin_user": ctx.pop("admin_user", None),
            "can_manage_users": bool(ctx.pop("can_manage_users", False)),
            "flash": flash,
            "flash_kind": flash_kind,
            "flash_details": flash_details,
            "static_v": static_v,
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
def admin_root(_: AdminPanelUser = Depends(require_admin_session)):
    return _redir("/admin/posts")

@router.get("/login")
def admin_login_get(request: Request, db=Depends(get_db)):
    _ensure_bootstrap_user(db)
    next_url = request.query_params.get("next") or "/admin/posts"
    flash = request.query_params.get("flash")
    flash_kind = request.query_params.get("kind")
    flash_details = request.query_params.get("details")
    static_v = (os.getenv("ADMIN_STATIC_VERSION") or "").strip() or "dev"
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "next_url": next_url,
            "flash": flash,
            "flash_kind": flash_kind,
            "flash_details": flash_details,
            "static_v": static_v,
        },
    )


@router.post("/login")
def admin_login_post(
    username: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("/admin/posts"),
    db=Depends(get_db),
):
    _ensure_bootstrap_user(db)
    _admin_secret()
    u = db.query(AdminPanelUser).filter(AdminPanelUser.username == username.strip()).first()
    if not u or not u.is_active:
        return _redir("/admin/login", flash="Неверный логин или пароль", kind="bad")
    if not _pbkdf2_verify(password, u.password_hash):
        return _redir("/admin/login", flash="Неверный логин или пароль", kind="bad")

    token = _make_session_token(u.id, int(u.session_version or 0))
    resp = _redir(next_url or "/admin/posts", flash="Вход выполнен", kind="ok")
    resp.set_cookie("admin_session", token, httponly=True, samesite="lax", secure=True, path="/admin")
    return resp


@router.post("/logout")
def admin_logout():
    resp = _redir("/admin/login", flash="Вы вышли", kind="ok")
    resp.delete_cookie("admin_session", path="/admin")
    return resp


@router.get("/posts")
def admin_posts(request: Request, user: AdminPanelUser = Depends(require_scope("posts:view")), db=Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(200).all()
    return _render(
        request,
        "posts.html",
        section="posts",
        title="Admin · Посты",
        posts=posts,
        admin_user=f"{user.username} · {user.role}",
        can_manage_users=_has_scope(user, "users"),
    )


@router.post("/posts/create")
def admin_posts_create(
    _: AdminPanelUser = Depends(require_scope("posts:write")),
    db=Depends(get_db),
    title: str = Form(...),
    content: str = Form(...),
):
    p = Post(title=title.strip(), content=content.strip())
    db.add(p)
    db.commit()
    return _redir("/admin/posts", flash="Пост создан", kind="ok")


@router.post("/posts/{post_id}/delete")
def admin_posts_delete(post_id: int, _: AdminPanelUser = Depends(require_scope("posts:delete")), db=Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        return _redir("/admin/posts", flash="Пост не найден", kind="bad")
    db.delete(p)
    db.commit()
    return _redir("/admin/posts", flash=f"Пост {post_id} удалён", kind="ok")


@router.get("/webinars")
def admin_webinars(request: Request, user: AdminPanelUser = Depends(require_scope("webinars:view")), db=Depends(get_db)):
    webinars = db.query(Webinar).order_by(Webinar.id.desc()).limit(200).all()
    return _render(
        request,
        "webinars.html",
        section="webinars",
        title="Admin · Вебинары",
        webinars=webinars,
        admin_user=f"{user.username} · {user.role}",
        can_manage_users=_has_scope(user, "users"),
    )


@router.post("/webinars/create")
def admin_webinars_create(
    _: AdminPanelUser = Depends(require_scope("webinars:write")),
    db=Depends(get_db),
    title: str = Form(...),
    date_: str = Form(..., alias="date"),
    time: str = Form(...),
    duration: str = Form(""),
    speaker: str = Form(""),
    status: str = Form("upcoming"),
    description: str = Form(""),
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
        # Вебинары бесплатные
        price_usd=0.0,
        price_eur=0.0,
        meeting_link=(meeting_link or "").strip() or None,
        meeting_platform=None,
        recording_link=None,
    )
    db.add(w)
    db.commit()
    return _redir("/admin/webinars", flash="Вебинар создан", kind="ok")


@router.post("/webinars/{webinar_id}/delete")
def admin_webinars_delete(webinar_id: int, _: AdminPanelUser = Depends(require_scope("webinars:delete")), db=Depends(get_db)):
    w = db.query(Webinar).filter(Webinar.id == webinar_id).first()
    if not w:
        return _redir("/admin/webinars", flash="Вебинар не найден", kind="bad")
    db.delete(w)
    db.commit()
    return _redir("/admin/webinars", flash=f"Вебинар {webinar_id} удалён", kind="ok")


@router.get("/tickets")
def admin_tickets(request: Request, user: AdminPanelUser = Depends(require_scope("tickets:view")), db=Depends(get_db)):
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
        admin_user=f"{user.username} · {user.role}",
        can_manage_users=_has_scope(user, "users"),
    )


@router.post("/tickets/{ticket_id}/respond")
def admin_ticket_respond(
    ticket_id: int,
    _: AdminPanelUser = Depends(require_scope("tickets:respond")),
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
def admin_admins(request: Request, user: AdminPanelUser = Depends(require_scope("admins:manage")), db=Depends(get_db)):
    admins = db.query(Admin).order_by(Admin.id.asc()).all()
    return _render(
        request,
        "admins.html",
        section="admins",
        title="Admin · Админы",
        admins=admins,
        admin_user=f"{user.username} · {user.role}",
        can_manage_users=_has_scope(user, "users"),
    )


@router.post("/admins/create")
def admin_admins_create(
    _: AdminPanelUser = Depends(require_scope("admins:manage")),
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
    _: AdminPanelUser = Depends(require_scope("admins:manage")),
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
def admin_admins_delete(admin_id: int, _: AdminPanelUser = Depends(require_scope("admins:manage")), db=Depends(get_db)):
    a = db.query(Admin).filter(Admin.id == admin_id).first()
    if not a:
        return _redir("/admin/admins", flash="Админ не найден", kind="bad")
    db.delete(a)
    db.commit()
    return _redir("/admin/admins", flash="Админ удалён", kind="ok")


@router.get("/data")
def admin_data(request: Request, user: AdminPanelUser = Depends(require_scope("data:view")), db=Depends(get_db)):
    tables = [t.name for t in Base.metadata.sorted_tables]

    # High-signal counts + recent rows (so you can see what exists)
    counts = {
        "users": db.query(User).count(),
        "admins": db.query(Admin).count(),
        "posts": db.query(Post).count(),
        "webinars": db.query(Webinar).count(),
        "bookings": db.query(Booking).count(),
        "payments": db.query(Payment).count(),
        "referrals": db.query(ReferralInvite).count(),
    }

    recent_users = db.query(User).order_by(User.id.desc()).limit(20).all()
    recent_posts = db.query(Post).order_by(Post.id.desc()).limit(20).all()
    recent_webinars = db.query(Webinar).order_by(Webinar.id.desc()).limit(20).all()
    recent_bookings = db.query(Booking).order_by(Booking.id.desc()).limit(20).all()
    recent_payments = db.query(Payment).order_by(Payment.id.desc()).limit(20).all()
    recent_referrals = db.query(ReferralInvite).order_by(ReferralInvite.id.desc()).limit(20).all()

    return _render(
        request,
        "data.html",
        section="data",
        title="Admin · Данные",
        tables=tables,
        counts=counts,
        recent_users=recent_users,
        recent_posts=recent_posts,
        recent_webinars=recent_webinars,
        recent_bookings=recent_bookings,
        recent_payments=recent_payments,
        recent_referrals=recent_referrals,
        admin_user=f"{user.username} · {user.role}",
        can_manage_users=_has_scope(user, "users"),
    )


@router.post("/data/clear-db")
def admin_clear_db(_: AdminPanelUser = Depends(require_scope("data:delete")), db=Depends(get_db)):
    deleted = _clear_all_tables(db)
    db.commit()
    return _redir("/admin/data", flash="База очищена", kind="ok", details=f"deleted_rows={deleted}")


@router.post("/data/clear-selected")
def admin_clear_selected(
    _: AdminPanelUser = Depends(require_scope("data:delete")),
    db=Depends(get_db),
    targets: list[str] = Form(...),
):
    targets_set = {t.strip() for t in (targets or []) if t and t.strip()}
    deleted, details = _clear_selected_tables(db, targets_set)
    db.commit()
    return _redir("/admin/data", flash="Выбранные данные удалены", kind="ok", details=f"deleted_rows={deleted}")


@router.get("/users")
def admin_panel_users(
    request: Request,
    user: AdminPanelUser = Depends(require_scope("users:manage")),
    db=Depends(get_db),
):
    users = db.query(AdminPanelUser).order_by(AdminPanelUser.id.asc()).all()
    user_scopes = {u.id: _user_scopes(u) for u in users}
    selected_id_raw = (request.query_params.get("u") or "").strip()
    selected_id = int(selected_id_raw) if selected_id_raw.isdigit() else None
    selected_user = None
    if selected_id is not None:
        selected_user = next((x for x in users if x.id == selected_id), None)
    if selected_user is None and users:
        selected_user = users[0]
    return _render(
        request,
        "users.html",
        section="users",
        title="Admin · Пользователи панели",
        users=users,
        selected_user=selected_user,
        perms=ADMIN_PERMS,
        user_scopes=user_scopes,
        admin_user=f"{user.username} · {user.role}",
        can_manage_users=True,
    )


@router.post("/users/create")
def admin_panel_users_create(
    user: AdminPanelUser = Depends(require_scope("users:manage")),
    db=Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("admin"),
    scopes: str = Form(""),
    perms: list[str] | None = Form(None),
):
    username = username.strip()
    if not username:
        return _redir("/admin/users", flash="Пустой username", kind="bad")
    if db.query(AdminPanelUser).filter(AdminPanelUser.username == username).first():
        return _redir("/admin/users", flash="Такой username уже есть", kind="bad")

    u = AdminPanelUser(
        username=username,
        password_hash=_pbkdf2_hash_password(password),
        role=(role or "admin").strip(),
        scopes=_perms_to_scopes(perms) or _normalize_scopes(scopes),
        is_active=True,
        session_version=0,
    )
    db.add(u)
    db.commit()
    return _redir("/admin/users", flash="Пользователь создан", kind="ok")


@router.post("/users/{user_id}/update")
def admin_panel_users_update(
    user_id: int,
    _: AdminPanelUser = Depends(require_scope("users:manage")),
    db=Depends(get_db),
    role: str = Form("admin"),
    scopes: str = Form(""),
    perms: list[str] | None = Form(None),
    is_active: str | None = Form(None),
):
    target = db.query(AdminPanelUser).filter(AdminPanelUser.id == user_id).first()
    if not target:
        return _redir("/admin/users", flash="Пользователь не найден", kind="bad")

    target.role = (role or "admin").strip()
    target.scopes = _perms_to_scopes(perms) or _normalize_scopes(scopes)
    target.is_active = bool(is_active)
    db.commit()
    return _redir("/admin/users", flash="Сохранено", kind="ok")


@router.post("/users/{user_id}/reset-password")
def admin_panel_users_reset_password(
    user_id: int,
    _: AdminPanelUser = Depends(require_scope("users:manage")),
    db=Depends(get_db),
    new_password: str = Form(...),
):
    target = db.query(AdminPanelUser).filter(AdminPanelUser.id == user_id).first()
    if not target:
        return _redir("/admin/users", flash="Пользователь не найден", kind="bad")
    target.password_hash = _pbkdf2_hash_password(new_password)
    target.session_version = int(target.session_version or 0) + 1
    db.commit()
    return _redir("/admin/users", flash="Пароль обновлён (сессии сброшены)", kind="ok")


@router.post("/users/{user_id}/delete")
def admin_panel_users_delete(
    user_id: int,
    acting: AdminPanelUser = Depends(require_scope("users:manage")),
    db=Depends(get_db),
):
    target = db.query(AdminPanelUser).filter(AdminPanelUser.id == user_id).first()
    if not target:
        return _redir("/admin/users", flash="Пользователь не найден", kind="bad")
    if target.id == acting.id:
        return _redir("/admin/users", flash="Нельзя удалить самого себя", kind="bad")
    db.delete(target)
    db.commit()
    return _redir("/admin/users", flash="Пользователь удалён", kind="ok")


# --- Balance / Deposit requests ---


def _limit_safe(limit_raw, default=50, max_val=100):
    try:
        n = int(limit_raw)
        return min(max(n, 1), max_val) if n > 0 else default
    except (TypeError, ValueError):
        return default


@router.get("/balance-requests")
def admin_balance_requests(
    request: Request,
    user: AdminPanelUser = Depends(require_scope("balance:view")),
    db=Depends(get_db),
):
    status_filter = (request.query_params.get("status") or "pending").strip().lower()
    if status_filter not in ("pending", "approved", "rejected", "all"):
        status_filter = "pending"
    limit = _limit_safe(request.query_params.get("limit"), 50, 100)
    page = max(1, int(request.query_params.get("page") or 1))

    q = db.query(BalanceRequest)
    if status_filter != "all":
        q = q.filter(BalanceRequest.status == status_filter)
    q = q.order_by(BalanceRequest.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()

    def to_ctx(r):
        u = db.query(User).filter(User.id == r.user_id).first()
        return {
            "id": r.id,
            "user_id": r.user_id,
            "user_telegram_id": u.telegram_id if u else None,
            "user_first_name": u.first_name if u else None,
            "user_username": u.username if u else None,
            "tx_ref": r.tx_ref,
            "status": r.status,
            "created_at": r.created_at,
        }

    pages = (total + limit - 1) // limit if limit else 0
    return _render(
        request,
        "balance_requests.html",
        section="balance_requests",
        title="Admin · Заявки на пополнение",
        items=[to_ctx(r) for r in items],
        page=page,
        pages=pages,
        total=total,
        limit=limit,
        status_filter=status_filter,
        admin_user=f"{user.username} · {user.role}",
        can_manage_users=_has_scope(user, "users"),
    )


@router.get("/balance-requests/{req_id}")
def admin_balance_request_detail(
    request: Request,
    req_id: int,
    user: AdminPanelUser = Depends(require_scope("balance:view")),
    db=Depends(get_db),
):
    r = db.query(BalanceRequest).filter(BalanceRequest.id == req_id).first()
    if not r:
        return _redir("/admin/balance-requests", flash="Заявка не найдена", kind="bad")
    u = db.query(User).filter(User.id == r.user_id).first()
    can_manage = _has_scope(user, "balance:manage")
    return _render(
        request,
        "balance_request_detail.html",
        section="balance_requests",
        title=f"Admin · Заявка #{r.id}",
        req=r,
        user=u,
        can_manage=can_manage,
        admin_user=f"{user.username} · {user.role}",
    )


@router.post("/balance-requests/{req_id}/approve")
def admin_balance_request_approve(
    req_id: int,
    acting: AdminPanelUser = Depends(require_scope("balance:manage")),
    db=Depends(get_db),
    amount: str = Form(...),
    comment: str = Form(""),
):
    try:
        amount_cents = parse_money(amount.strip())
        if amount_cents <= 0:
            return _redir(f"/admin/balance-requests/{req_id}", flash="Сумма должна быть положительной", kind="bad")
    except ValueError as e:
        return _redir(f"/admin/balance-requests/{req_id}", flash=str(e), kind="bad")
    try:
        approve_deposit_request(db, req_id, amount_cents, acting.id, comment or None)
        return _redir("/admin/balance-requests", flash="Заявка одобрена", kind="ok")
    except ValueError as e:
        return _redir(f"/admin/balance-requests/{req_id}", flash=str(e), kind="bad")


@router.post("/balance-requests/{req_id}/reject")
def admin_balance_request_reject(
    req_id: int,
    acting: AdminPanelUser = Depends(require_scope("balance:manage")),
    db=Depends(get_db),
    comment: str = Form(""),
):
    try:
        reject_deposit_request(db, req_id, acting.id, comment or None)
        return _redir("/admin/balance-requests", flash="Заявка отклонена", kind="ok")
    except ValueError as e:
        return _redir(f"/admin/balance-requests/{req_id}", flash=str(e), kind="bad")


@router.get("/app-users")
def admin_app_users(
    request: Request,
    user: AdminPanelUser = Depends(require_scope("balance:view")),
    db=Depends(get_db),
):
    search = (request.query_params.get("search") or "").strip()
    limit = _limit_safe(request.query_params.get("limit"), 50, 100)
    page = max(1, int(request.query_params.get("page") or 1))

    from sqlalchemy import or_

    q = db.query(User)
    if search:
        like = f"%{search}%"
        conds = [User.username.ilike(like), User.first_name.ilike(like), User.last_name.ilike(like)]
        if search.isdigit():
            conds.append(User.telegram_id == int(search))
        q = q.filter(or_(*conds))
    q = q.order_by(User.id.desc())
    total = q.count()
    users = q.offset((page - 1) * limit).limit(limit).all()

    def to_ctx(u):
        balance = get_balance_cents(db, u.id)
        return {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_blocked": u.is_blocked,
            "balance_cents": balance,
            "balance_formatted": _format_money(balance),
        }

    pages = (total + limit - 1) // limit if limit else 0
    return _render(
        request,
        "app_users.html",
        section="app_users",
        title="Admin · Пользователи приложения",
        users=[to_ctx(u) for u in users],
        page=page,
        pages=pages,
        total=total,
        limit=limit,
        search=search,
        admin_user=f"{user.username} · {user.role}",
    )


@router.get("/app-users/{user_id}")
def admin_app_user_profile(
    request: Request,
    user_id: int,
    acting: AdminPanelUser = Depends(require_scope("balance:view")),
    db=Depends(get_db),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return _redir("/admin/app-users", flash="Пользователь не найден", kind="bad")
    balance = get_balance_cents(db, u.id)
    can_manage = _has_scope(acting, "balance:manage")

    ledger_page = max(1, int(request.query_params.get("ledger_page") or 1))
    ledger_limit = _limit_safe(request.query_params.get("ledger_limit"), 50, 100)
    ledger_q = db.query(BalanceLedger).filter(BalanceLedger.user_id == user_id).order_by(BalanceLedger.created_at.desc())
    ledger_total = ledger_q.count()
    ledger_items = ledger_q.offset((ledger_page - 1) * ledger_limit).limit(ledger_limit).all()
    ledger_pages = (ledger_total + ledger_limit - 1) // ledger_limit if ledger_limit else 0

    return _render(
        request,
        "app_user_profile.html",
        section="app_users",
        title=f"Admin · Пользователь #{u.id}",
        target_user=u,
        balance_cents=balance,
        balance_formatted=_format_money(balance),
        can_manage=can_manage,
        ledger_items=ledger_items,
        ledger_page=ledger_page,
        ledger_pages=ledger_pages,
        ledger_total=ledger_total,
        ledger_limit=ledger_limit,
        admin_user=f"{acting.username} · {acting.role}",
    )


@router.post("/app-users/{user_id}/block")
def admin_app_user_block(
    user_id: int,
    acting: AdminPanelUser = Depends(require_scope("balance:manage")),
    db=Depends(get_db),
    blocked: str = Form("0"),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return _redir("/admin/app-users", flash="Пользователь не найден", kind="bad")
    u.is_blocked = str(blocked).strip() == "1"
    db.commit()
    return _redir(f"/admin/app-users/{user_id}", flash="Статус блокировки обновлён", kind="ok")


@router.post("/app-users/{user_id}/balance-adjust")
def admin_app_user_balance_adjust(
    user_id: int,
    acting: AdminPanelUser = Depends(require_scope("balance:manage")),
    db=Depends(get_db),
    delta: str = Form(...),
    comment: str = Form(""),
):
    try:
        delta_cents = parse_money(delta.strip())
        if delta_cents == 0:
            return _redir(f"/admin/app-users/{user_id}", flash="Дельта не должна быть 0", kind="bad")
    except ValueError as e:
        return _redir(f"/admin/app-users/{user_id}", flash=str(e), kind="bad")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return _redir("/admin/app-users", flash="Пользователь не найден", kind="bad")
    try:
        admin_adjust_balance(db, user_id, delta_cents, acting.id, comment or None)
        return _redir(f"/admin/app-users/{user_id}", flash="Баланс изменён", kind="ok")
    except ValueError as e:
        return _redir(f"/admin/app-users/{user_id}", flash=str(e), kind="bad")

