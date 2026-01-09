"""
Миграция для добавления полей оплаты в таблицу bookings
"""
import sqlite3
import os

# Путь к базе данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

def migrate():
    """Добавляет новые колонки в таблицу bookings"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем существующие колонки
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print("Существующие колонки:", columns)
        
        # Добавляем новые колонки, если их еще нет
        new_columns = [
            ("payment_status", "TEXT DEFAULT 'unpaid'"),
            ("amount", "REAL"),
            ("payment_id", "TEXT"),
            ("payment_date", "DATETIME"),
            ("reminder_sent_24h", "INTEGER DEFAULT 0"),
            ("reminder_sent_1h", "INTEGER DEFAULT 0"),
            ("reminder_sent_10m", "INTEGER DEFAULT 0"),
            ("attended", "INTEGER DEFAULT 0"),
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE bookings ADD COLUMN {column_name} {column_type}")
                    print(f"[OK] Добавлена колонка: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"[ERROR] Ошибка при добавлении {column_name}: {e}")
            else:
                print(f"[SKIP] Колонка {column_name} уже существует")
        
        # Обновляем статус существующих записей
        cursor.execute("""
            UPDATE bookings 
            SET status = 'pending' 
            WHERE status = 'active' AND payment_status IS NULL
        """)
        
        conn.commit()
        print("\n[SUCCESS] Миграция успешно завершена!")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Ошибка при миграции: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Запуск миграции для таблицы bookings...")
    migrate()
