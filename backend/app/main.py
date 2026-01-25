import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler

from app.routers import users, bookings, webinars, admins, posts, payments, webinar_materials, reminders, referrals, nowpayments

from app.database import engine, Base
from app.models import User, Booking, Webinar, Admin, Post, Payment, WebinarMaterial, ReferralInvite

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crypto Analytics API")

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
# Настройка CORS - разрешаем все источники и методы
# Для ngrok важно разрешить все origins, так как URL может меняться
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники (включая ngrok)
    allow_credentials=False,  # Отключаем credentials (несовместимо с "*")
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки (включая ngrok-specific)
    expose_headers=["*"],  # Разрешаем доступ ко всем заголовкам ответа
)

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
app.include_router(nowpayments.compat_router)