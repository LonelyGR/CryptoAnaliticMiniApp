"""
Скрипт для удаления всех тестовых данных из базы данных
ВНИМАНИЕ: Этот скрипт удалит все вебинары, бронирования и пользователей (кроме админов)
"""
import sys
from app.database import SessionLocal
from app.models.booking import Booking
from app.models.webinar import Webinar
from app.models.user import User
from app.models.admin import Admin

def remove_test_data():
    db = SessionLocal()
    try:
        # Сначала проверяем структуру таблицы bookings
        # Если новых колонок нет, используем старую модель
        try:
            # Пытаемся выполнить запрос с новыми полями
            test_query = db.query(Booking).first()
            bookings_count = db.query(Booking).count()
        except Exception as e:
            if 'admin_response' in str(e) or 'admin_id' in str(e):
                print("WARNING: Таблица bookings не имеет новых колонок (admin_response, admin_id)")
                print("Выполните миграцию: python migrate_bookings_sqlalchemy.py")
                print("Или запустите приложение - оно создаст правильную структуру")
                return False
            else:
                raise
        
        webinars_count = db.query(Webinar).count()
        users_count = db.query(User).count()
        admins_count = db.query(Admin).count()
        
        print("Текущее состояние базы данных:")
        print(f"   Бронирования: {bookings_count}")
        print(f"   Вебинары: {webinars_count}")
        print(f"   Пользователи: {users_count}")
        print(f"   Администраторы: {admins_count}")
        print()
        
        # Получаем telegram_id всех админов, чтобы не удалить их
        admin_telegram_ids = {admin.telegram_id for admin in db.query(Admin).all()}
        print(f"OK: Защищены от удаления: {len(admin_telegram_ids)} администраторов")
        print()
        
        # Удаляем все бронирования
        deleted_bookings = db.query(Booking).delete()
        print(f"Удалено бронирований: {deleted_bookings}")
        
        # Удаляем все вебинары
        deleted_webinars = db.query(Webinar).delete()
        print(f"Удалено вебинаров: {deleted_webinars}")
        
        # Удаляем всех пользователей, кроме админов
        users_to_delete = db.query(User).filter(~User.telegram_id.in_(admin_telegram_ids)).all()
        deleted_users = len(users_to_delete)
        for user in users_to_delete:
            db.delete(user)
        print(f"Удалено пользователей: {deleted_users}")
        
        db.commit()
        
        print()
        print("OK: Тестовые данные успешно удалены!")
        print()
        print("Состояние базы данных после очистки:")
        print(f"   Администраторы: {admins_count} (не удалены)")
        print(f"   Пользователи: {db.query(User).count()}")
        print(f"   Вебинары: {db.query(Webinar).count()}")
        print(f"   Бронирования: {db.query(Booking).count()}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при удалении данных: {e}")
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    print("ВНИМАНИЕ: Этот скрипт удалит все тестовые данные!")
    print("   Администраторы будут сохранены.")
    print()
    
    response = input("Продолжить? (yes/no): ")
    if response.lower() not in ['yes', 'y', 'да', 'д']:
        print("Отменено.")
        sys.exit(0)
    
    print()
    remove_test_data()

