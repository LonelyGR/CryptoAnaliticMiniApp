"""
Скрипт для полной очистки базы данных без удаления таблиц.
Удаляет все строки во всех таблицах (структура сохраняется).
"""
import sys
from sqlalchemy import text
from app.database import SessionLocal, Base
from app.models import admin, booking, payment, post, referral_invite, user, webinar_material, webinar  # noqa: F401


def clear_db():
    db = SessionLocal()
    try:
        # Временное отключение FK для корректной очистки
        db.execute(text("PRAGMA foreign_keys=OFF"))

        total_deleted = 0
        for table in reversed(Base.metadata.sorted_tables):
            result = db.execute(table.delete())
            deleted = result.rowcount if result.rowcount is not None else 0
            total_deleted += deleted
            print(f"Очищено {table.name}: {deleted}")

        db.commit()
        db.execute(text("PRAGMA foreign_keys=ON"))
        print()
        print(f"OK: База очищена. Всего удалено строк: {total_deleted}")
    except Exception as exc:
        db.rollback()
        print(f"❌ Ошибка при очистке базы: {exc}")
        return False
    finally:
        db.close()
    return True


if __name__ == "__main__":
    print("ВНИМАНИЕ: Скрипт полностью удалит данные из ВСЕХ таблиц!")
    response = input("Продолжить? (yes/no): ")
    if response.lower() not in ["yes", "y", "да", "д"]:
        print("Отменено.")
        sys.exit(0)

    clear_db()
