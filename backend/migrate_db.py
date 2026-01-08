"""
Скрипт для обновления структуры базы данных
Использование: python migrate_db.py
"""
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "db.sqlite3"

def backup_database():
    """Создание резервной копии базы данных"""
    if DB_PATH.exists():
        backup_path = BASE_DIR / "db.sqlite3.backup"
        print(f"Создание резервной копии: {backup_path}")
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print("[OK] Резервная копия создана")
        return True
    return False

def check_columns(conn, table_name, required_columns):
    """Проверка наличия колонок в таблице"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [row[1] for row in cursor.fetchall()]
    missing_columns = [col for col in required_columns if col not in existing_columns]
    return missing_columns, existing_columns

def migrate_database():
    """Миграция базы данных"""
    print("="*60)
    print("МИГРАЦИЯ БАЗЫ ДАННЫХ")
    print("="*60)
    
    if not DB_PATH.exists():
        print("База данных не найдена. Она будет создана при следующем запуске сервера.")
        return True
    
    # Создаем резервную копию
    backup_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем таблицу users
        print("\n[1/2] Проверка таблицы users...")
        users_missing, users_existing = check_columns(conn, "users", [
            "id", "telegram_id", "username", "first_name", "last_name", "photo_url"
        ])
        
        if users_missing:
            print(f"   Найдены отсутствующие колонки: {users_missing}")
            if "last_name" in users_missing:
                print("   Добавление колонки last_name...")
                cursor.execute("ALTER TABLE users ADD COLUMN last_name VARCHAR")
            if "photo_url" in users_missing:
                print("   Добавление колонки photo_url...")
                cursor.execute("ALTER TABLE users ADD COLUMN photo_url VARCHAR")
            print("   [OK] Таблица users обновлена")
        else:
            print("   [OK] Таблица users в порядке")
        
        # Проверяем таблицу bookings
        print("\n[2/2] Проверка таблицы bookings...")
        bookings_missing, bookings_existing = check_columns(conn, "bookings", [
            "id", "user_id", "webinar_id", "type", "date", "time", "status", "topic", "message"
        ])
        
        if bookings_missing:
            print(f"   Найдены отсутствующие колонки: {bookings_missing}")
            if "webinar_id" in bookings_missing:
                print("   Добавление колонки webinar_id...")
                cursor.execute("ALTER TABLE bookings ADD COLUMN webinar_id INTEGER")
            if "time" in bookings_missing:
                print("   Добавление колонки time...")
                cursor.execute("ALTER TABLE bookings ADD COLUMN time VARCHAR")
            if "topic" in bookings_missing:
                print("   Добавление колонки topic...")
                cursor.execute("ALTER TABLE bookings ADD COLUMN topic VARCHAR")
            if "message" in bookings_missing:
                print("   Добавление колонки message...")
                cursor.execute("ALTER TABLE bookings ADD COLUMN message VARCHAR")
            print("   [OK] Таблица bookings обновлена")
        else:
            print("   [OK] Таблица bookings в порядке")
        
        # Проверяем таблицу webinars (может не существовать)
        print("\n[3/3] Проверка таблицы webinars...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='webinars'")
        if cursor.fetchone():
            print("   [OK] Таблица webinars существует")
        else:
            print("   ⚠ Таблица webinars не найдена (будет создана при запуске сервера)")
        
        conn.commit()
        print("\n" + "="*60)
        print("МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("="*60)
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ ОШИБКА при миграции: {e}")
        print("Резервная копия сохранена: db.sqlite3.backup")
        return False
    finally:
        conn.close()

def recreate_database():
    """Пересоздание базы данных (удаление и создание заново)"""
    print("="*60)
    print("ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ")
    print("="*60)
    print("⚠ ВНИМАНИЕ: Все данные будут удалены!")
    
    if DB_PATH.exists():
        backup_database()
        print(f"\nУдаление старой базы данных...")
        DB_PATH.unlink()
        print("[OK] Старая база данных удалена")
    
    print("\nБаза данных будет создана автоматически при следующем запуске сервера.")
    print("="*60)
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--recreate":
        # Пересоздание базы данных
        response = input("Вы уверены? Все данные будут удалены! (yes/no): ")
        if response.lower() == "yes":
            recreate_database()
        else:
            print("Отменено.")
    else:
        # Обычная миграция
        success = migrate_database()
        if not success:
            print("\nЕсли миграция не помогла, попробуйте пересоздать базу:")
            print("  python migrate_db.py --recreate")
            sys.exit(1)

