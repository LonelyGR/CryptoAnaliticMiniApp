from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, bookings, webinars

from app.database import engine, Base
from app.models import User, Booking, Webinar

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crypto Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"Status": "OK", "message": "Crypto Analytics API is running"}

app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(webinars.router)