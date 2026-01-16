"""
Миграция для системы рефералов.
Добавляет колонки users.referral_code, users.referred_by_telegram_id
и создает таблицу referral_invites.
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "db.sqlite3"


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return column_name in [row[1] for row in cursor.fetchall()]


def table_exists(cursor, table_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def migrate():
    if not DB_PATH.exists():
        print("База данных не найдена. Она будет создана при запуске сервера.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if not column_exists(cursor, "users", "referral_code"):
            print("Добавляем колонку referral_code в users...")
            cursor.execute("ALTER TABLE users ADD COLUMN referral_code VARCHAR")

        if not column_exists(cursor, "users", "referred_by_telegram_id"):
            print("Добавляем колонку referred_by_telegram_id в users...")
            cursor.execute("ALTER TABLE users ADD COLUMN referred_by_telegram_id INTEGER")

        if not table_exists(cursor, "referral_invites"):
            print("Создаем таблицу referral_invites...")
            cursor.execute(
                """
                CREATE TABLE referral_invites (
                    id INTEGER PRIMARY KEY,
                    referrer_telegram_id INTEGER NOT NULL,
                    referred_telegram_id INTEGER,
                    referred_username VARCHAR,
                    referred_first_name VARCHAR,
                    referred_last_name VARCHAR,
                    created_at DATETIME
                )
                """
            )

        conn.commit()
        print("Миграция рефералов завершена успешно.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка миграции: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
