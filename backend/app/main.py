import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.routers import users, bookings, webinars, admins, posts, payments, webinar_materials, reminders, referrals, nowpayments, admin_panel, product_payments, debug

from app.database import engine, Base
from app.models import User, Booking, Webinar, Admin, Post, Payment, WebinarMaterial, ReferralInvite

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crypto Analytics API")

_root_logger = logging.getLogger()
if not _root_logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
logger = logging.getLogger("app")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Прод-режим: не логируем body без явного флага (может содержать PII/секреты).
    if os.getenv("DEBUG_VALIDATION_ERRORS") == "1":
        logger.warning("REQUEST VALIDATION ERROR detail=%s", exc.errors())
        try:
            logger.warning("REQUEST VALIDATION ERROR body=%s", exc.body)
        except Exception:
            pass
    return await request_validation_exception_handler(request, exc)


def _get_domain() -> str:
    return (os.getenv("DOMAIN") or "").strip()


def _get_allowed_hosts() -> list[str]:
    """
    Protect against Host header attacks.
    - In prod: set DOMAIN and we only allow that host (+ www).
    - In dev: allow all.
    """
    domain = _get_domain()
    if not domain:
        return ["*"]
    return [domain, f"www.{domain}"]


def _get_cors_origins() -> list[str]:
    """
    CORS origins for production.
    - If CORS_ALLOW_ORIGINS is set (comma-separated), use it.
    - Else if DOMAIN is set, allow only https://<DOMAIN> and https://www.<DOMAIN>.
    - Else: allow none (fail closed).
    """
    raw = (os.getenv("CORS_ALLOW_ORIGINS") or "").strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    domain = _get_domain()
    if domain:
        return [f"https://{domain}", f"https://www.{domain}"]
    return []


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=False,  # Отключаем credentials (несовместимо с "*")
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки (включая ngrok-specific)
    expose_headers=["*"],  # Разрешаем доступ ко всем заголовкам ответа
)


# Trusted hosts (works well behind reverse-proxy when DOMAIN is configured)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=_get_allowed_hosts())


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    resp: Response = await call_next(request)
    # Minimal safe headers for API responses (edge proxy also adds headers).
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    return resp


@app.get("/")
def root():
    return {"Status": "OK", "message": "Crypto Analytics API is running"}

app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(webinars.router)
app.include_router(admins.router)
app.include_router(posts.router)
app.include_router(payments.router)
app.include_router(webinar_materials.router)
app.include_router(reminders.router)
app.include_router(referrals.router)
app.include_router(nowpayments.router)
app.include_router(admin_panel.router)
app.include_router(product_payments.router)
app.include_router(debug.router)

# Static assets for backend admin panel
_admin_static_dir = os.path.join(os.path.dirname(__file__), "admin_static")
if os.path.isdir(_admin_static_dir):
    app.mount("/admin/static", StaticFiles(directory=_admin_static_dir), name="admin-static")