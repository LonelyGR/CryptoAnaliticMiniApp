"""
Скрипт для создания администратора
Использование: python create_admin.py <telegram_id> <role>
Пример: python create_admin.py 123456789 "Главный администратор"
"""
import sys
from app.database import SessionLocal
from app.models.admin import Admin

def create_admin(telegram_id: int, role: str = "Администратор"):
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже админ с таким telegram_id
        existing_admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        if existing_admin:
            print(f"⚠️  Админ с telegram_id {telegram_id} уже существует!")
            print(f"   ID: {existing_admin.id}")
            print(f"   Роль: {existing_admin.role}")
            # Обновляем роль если нужно
            if existing_admin.role != role:
                existing_admin.role = role
                db.commit()
                print(f"✅ Роль обновлена на: {role}")
            return existing_admin
        
        # Создаем нового админа
        admin = Admin(telegram_id=telegram_id, role=role)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"✅ Админ успешно создан!")
        print(f"   ID: {admin.id}")
        print(f"   Telegram ID: {admin.telegram_id}")
        print(f"   Роль: {admin.role}")
        return admin
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании админа: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python create_admin.py <telegram_id> [role]")
        print("Пример: python create_admin.py 123456789 \"Главный администратор\"")
        sys.exit(1)
    
    try:
        telegram_id = int(sys.argv[1])
        role = sys.argv[2] if len(sys.argv) > 2 else "Администратор"
        create_admin(telegram_id, role)
    except ValueError:
        print("❌ Ошибка: telegram_id должен быть числом")
        sys.exit(1)

