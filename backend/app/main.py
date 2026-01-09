from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, bookings, webinars, admins, posts, payments, webinar_materials, remindersмс

from app.database import engine, Base
from app.models import User, Booking, Webinar, Admin, Post, Payment, WebinarMaterial

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crypto Analytics API")
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