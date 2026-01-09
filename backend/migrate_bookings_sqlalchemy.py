"""
Скрипт для миграции таблицы bookings через SQLAlchemy
"""
from app.database import engine
from sqlalchemy import text

def migrate_bookings_table():
    """Добавляет колонки admin_response и admin_id в таблицу bookings"""
    
    with engine.connect() as conn:
        try:
            # Проверяем существующие колонки
            result = conn.execute(text("PRAGMA table_info(bookings)"))
            columns = [row[1] for row in result]
            
            print("Текущие колонки в таблице bookings:")
            for col in columns:
                print(f"   - {col}")
            print()
            
            # Добавляем admin_response если его нет
            if 'admin_response' not in columns:
                print("Добавляем колонку admin_response...")
                conn.execute(text("ALTER TABLE bookings ADD COLUMN admin_response TEXT"))
                conn.commit()
                print("OK: Колонка admin_response добавлена")
            else:
                print("OK: Колонка admin_response уже существует")
            
            # Добавляем admin_id если его нет
            if 'admin_id' not in columns:
                print("Добавляем колонку admin_id...")
                conn.execute(text("ALTER TABLE bookings ADD COLUMN admin_id INTEGER"))
                conn.commit()
                print("OK: Колонка admin_id добавлена")
            else:
                print("OK: Колонка admin_id уже существует")
            
            # Проверяем результат
            result = conn.execute(text("PRAGMA table_info(bookings)"))
            columns_after = [row[1] for row in result]
            
            print()
            print("Колонки после миграции:")
            for col in columns_after:
                print(f"   - {col}")
            print()
            print("OK: Миграция успешно завершена!")
            
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"ERROR: Ошибка при миграции: {e}")
            return False

if __name__ == "__main__":
    print("Миграция таблицы bookings...")
    print()
    migrate_bookings_table()

