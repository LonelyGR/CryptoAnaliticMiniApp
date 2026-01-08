"""
Скрипт для добавления таблицы admins в существующую базу данных
Использование: python migrate_db_admins.py
"""
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "db.sqlite3"

def migrate_admins_table():
    """Добавление таблицы admins если её нет"""
    print("="*60)
    print("МИГРАЦИЯ: Добавление таблицы admins")
    print("="*60)
    
    if not DB_PATH.exists():
        print("База данных не найдена. Она будет создана при следующем запуске сервера.")
        return True
    
    # Создаем резервную копию
    if DB_PATH.exists():
        backup_path = BASE_DIR / "db.sqlite3.backup_admins"
        print(f"Создание резервной копии: {backup_path}")
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print("[OK] Резервная копия создана")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли таблица admins
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admins'")
        if cursor.fetchone():
            print("[OK] Таблица admins уже существует")
        else:
            print("Создание таблицы admins...")
            cursor.execute("""
                CREATE TABLE admins (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE,
                    role VARCHAR NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX ix_admins_telegram_id ON admins (telegram_id)")
            print("[OK] Таблица admins создана")
        
        conn.commit()
        print("\n" + "="*60)
        print("МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("="*60)
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ ОШИБКА при миграции: {e}")
        print("Резервная копия сохранена: db.sqlite3.backup_admins")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    success = migrate_admins_table()
    sys.exit(0 if success else 1)

