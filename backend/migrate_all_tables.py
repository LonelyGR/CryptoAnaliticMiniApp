"""
Миграция для добавления новых полей во все таблицы
"""
import sqlite3
import os

# Путь к базе данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

def migrate_webinars():
    """Добавляет новые колонки в таблицу webinars"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(webinars)")
        columns = [row[1] for row in cursor.fetchall()]
        
        new_columns = [
            ("price", "REAL DEFAULT 0.0"),
            ("meeting_link", "TEXT"),
            ("meeting_platform", "TEXT"),
            ("recording_link", "TEXT"),
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE webinars ADD COLUMN {column_name} {column_type}")
                    print(f"[OK] Webinars: добавлена колонка {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"[ERROR] Webinars: ошибка при добавлении {column_name}: {e}")
            else:
                print(f"[SKIP] Webinars: колонка {column_name} уже существует")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Webinars: ошибка при миграции: {e}")
    finally:
        conn.close()

def migrate_payments():
    """Создает таблицу payments, если ее нет"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли таблица
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='payments'
        """)
        
        if cursor.fetchone():
            print("[SKIP] Таблица payments уже существует")
        else:
            # Создаем таблицу payments
            cursor.execute("""
                CREATE TABLE payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    webinar_id INTEGER,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    payment_method TEXT,
                    payment_provider TEXT,
                    transaction_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME,
                    completed_at DATETIME,
                    payment_metadata TEXT,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (webinar_id) REFERENCES webinars(id)
                )
            """)
            print("[OK] Таблица payments создана")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Payments: ошибка при миграции: {e}")
    finally:
        conn.close()

def migrate_webinar_materials():
    """Создает таблицу webinar_materials, если ее нет"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='webinar_materials'
        """)
        
        if cursor.fetchone():
            print("[SKIP] Таблица webinar_materials уже существует")
        else:
            cursor.execute("""
                CREATE TABLE webinar_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    webinar_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    file_url TEXT,
                    file_type TEXT,
                    created_at DATETIME,
                    FOREIGN KEY (webinar_id) REFERENCES webinars(id)
                )
            """)
            print("[OK] Таблица webinar_materials создана")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] WebinarMaterials: ошибка при миграции: {e}")
    finally:
        conn.close()

def migrate_posts():
    """Создает таблицу posts, если ее нет"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='posts'
        """)
        
        if cursor.fetchone():
            print("[SKIP] Таблица posts уже существует")
        else:
            cursor.execute("""
                CREATE TABLE posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """)
            print("[OK] Таблица posts создана")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Posts: ошибка при миграции: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Запуск полной миграции базы данных...\n")
    migrate_webinars()
    migrate_payments()
    migrate_webinar_materials()
    migrate_posts()
    print("\n[SUCCESS] Все миграции завершены!")
