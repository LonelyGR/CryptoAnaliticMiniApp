from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, bookings, webinars, admins

from app.database import engine, Base
from app.models import User, Booking, Webinar, Admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crypto Analytics API")
# Настройка CORS - разрешаем все источники и методы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=False,  # Отключаем credentials (несовместимо с "*")
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
    expose_headers=["*"],  # Разрешаем доступ ко всем заголовкам ответа
)

@app.get("/")
def root():
    return {"Status": "OK", "message": "Crypto Analytics API is running"}

app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(webinars.router)
app.include_router(admins.router)