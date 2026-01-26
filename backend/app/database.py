from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Путь к базе данных относительно папки backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Production-friendly:
# - Prefer DATABASE_URL from env (Postgres or SQLite)
# - Fallback to local SQLite in backend/ directory
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
