"""
Миграция: добавление колонки is_blocked в таблицу users.
Использование: python migrate_users_blocked.py
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "db.sqlite3"


def column_exists(conn, table_name, column_name):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return column_name in [row[1] for row in cursor.fetchall()]


def migrate():
    if not DB_PATH.exists():
        print("База данных не найдена. Запустите сервер для создания.")
        return True

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        if not column_exists(conn, "users", "is_blocked"):
            print("Добавление колонки is_blocked в users...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_blocked BOOLEAN NOT NULL DEFAULT 0")
            conn.commit()
            print("[OK] Колонка is_blocked добавлена")
        else:
            print("[OK] Колонка is_blocked уже существует")
        return True
    except Exception as exc:
        conn.rollback()
        print(f"✗ Ошибка миграции: {exc}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
