"""
Скрипт для миграции таблицы bookings - добавление полей для ответов администраторов
"""
import sqlite3
import os

# Путь к базе данных (как в database.py)
# database.py использует: BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# что означает корень проекта (на уровень выше backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

def migrate_bookings_table():
    """Добавляет колонки admin_response и admin_id в таблицу bookings"""
    
    if not os.path.exists(DATABASE_PATH):
        print(f"ERROR: База данных не найдена: {DATABASE_PATH}")
        print("База данных будет создана при первом запуске приложения.")
        print("Запустите приложение один раз, затем повторите миграцию.")
        return False
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли таблица bookings
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bookings'")
        if not cursor.fetchone():
            print("ERROR: Таблица bookings не найдена в базе данных.")
            print("Запустите приложение один раз для создания таблиц, затем повторите миграцию.")
            return False
        
        # Проверяем существующие колонки
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print("Текущие колонки в таблице bookings:")
        for col in columns:
            print(f"   - {col}")
        print()
        
        # Добавляем admin_response если его нет
        if 'admin_response' not in columns:
            print("Добавляем колонку admin_response...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN admin_response TEXT")
            print("OK: Колонка admin_response добавлена")
        else:
            print("OK: Колонка admin_response уже существует")
        
        # Добавляем admin_id если его нет
        if 'admin_id' not in columns:
            print("Добавляем колонку admin_id...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN admin_id INTEGER")
            print("OK: Колонка admin_id добавлена")
        else:
            print("OK: Колонка admin_id уже существует")
        
        conn.commit()
        
        # Проверяем результат
        cursor.execute("PRAGMA table_info(bookings)")
        columns_after = [column[1] for column in cursor.fetchall()]
        
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
    finally:
        conn.close()

if __name__ == "__main__":
    print("Миграция таблицы bookings...")
    print()
    migrate_bookings_table()
