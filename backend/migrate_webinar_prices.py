"""
Миграция для замены поля price на price_usd и price_eur в таблице webinars
"""
import sqlite3
import os

# Путь к базе данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

def migrate():
    """Заменяет price на price_usd и price_eur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем существующие колонки
        cursor.execute("PRAGMA table_info(webinars)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print("Существующие колонки:", columns)
        
        # Если есть старое поле price, сохраняем его значение
        old_price_value = None
        if 'price' in columns:
            cursor.execute("SELECT price FROM webinars LIMIT 1")
            result = cursor.fetchone()
            if result:
                old_price_value = result[0]
            print(f"[INFO] Найдено старое значение price: {old_price_value}")
        
        # Добавляем новые колонки, если их нет
        if 'price_usd' not in columns:
            try:
                cursor.execute("ALTER TABLE webinars ADD COLUMN price_usd REAL DEFAULT 0.0")
                print("[OK] Добавлена колонка: price_usd")
                
                # Если было старое значение price, копируем его в price_usd
                if old_price_value is not None:
                    cursor.execute("UPDATE webinars SET price_usd = price WHERE price IS NOT NULL")
                    print(f"[OK] Скопировано значение из price в price_usd: {old_price_value}")
            except sqlite3.OperationalError as e:
                print(f"[ERROR] Ошибка при добавлении price_usd: {e}")
        else:
            print("[SKIP] Колонка price_usd уже существует")
        
        if 'price_eur' not in columns:
            try:
                cursor.execute("ALTER TABLE webinars ADD COLUMN price_eur REAL DEFAULT 0.0")
                print("[OK] Добавлена колонка: price_eur")
            except sqlite3.OperationalError as e:
                print(f"[ERROR] Ошибка при добавлении price_eur: {e}")
        else:
            print("[SKIP] Колонка price_eur уже существует")
        
        # Удаляем старое поле price, если оно есть (опционально, можно оставить для совместимости)
        # Если хотите удалить, раскомментируйте:
        # if 'price' in columns:
        #     # SQLite не поддерживает DROP COLUMN напрямую, нужна пересоздание таблицы
        #     print("[INFO] Поле price оставлено для совместимости")
        
        conn.commit()
        print("\n[SUCCESS] Миграция успешно завершена!")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Ошибка при миграции: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Запуск миграции для таблицы webinars (цены)...")
    migrate()
