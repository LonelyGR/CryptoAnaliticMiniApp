"""
Скрипт для добавления первого администратора
Использование: python add_first_admin.py
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def add_first_admin():
    """Добавление первого администратора"""
    print("="*60)
    print("ДОБАВЛЕНИЕ ПЕРВОГО АДМИНИСТРАТОРА")
    print("="*60)
    
    # Данные первого админа
    admin_data = {
        "telegram_id": 6989481318,
        "role": "разработчик"
    }
    
    # Проверка доступности сервера
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("✗ ОШИБКА: Сервер недоступен!")
            print("Запустите сервер: cd backend && python run.py")
            return False
    except Exception as e:
        print(f"✗ ОШИБКА: Не удалось подключиться к серверу: {e}")
        print("Запустите сервер: cd backend && python run.py")
        return False
    
    print("✓ Сервер доступен\n")
    
    # Проверяем, существует ли уже админ
    try:
        response = requests.get(f"{BASE_URL}/admins/telegram/{admin_data['telegram_id']}", timeout=5)
        if response.status_code == 200:
            existing_admin = response.json()
            print(f"⚠ Администратор уже существует:")
            print(f"   ID: {existing_admin['id']}")
            print(f"   Telegram ID: {existing_admin['telegram_id']}")
            print(f"   Должность: {existing_admin['role']}")
            print("\nОбновление должности...")
            
            # Обновляем должность
            response = requests.post(
                f"{BASE_URL}/admins/",
                json=admin_data,
                timeout=5
            )
            if response.status_code == 200:
                updated_admin = response.json()
                print(f"✓ Должность обновлена: {updated_admin['role']}")
                return True
            else:
                print(f"✗ Ошибка обновления: {response.status_code}")
                return False
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # Админ не существует, создаем
            pass
        else:
            print(f"✗ Ошибка проверки: {e}")
            return False
    except Exception as e:
        print(f"⚠ Ошибка проверки существования админа: {e}")
        print("Продолжаем создание...")
    
    # Создаем админа
    print(f"Создание администратора:")
    print(f"   Telegram ID: {admin_data['telegram_id']}")
    print(f"   Должность: {admin_data['role']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/admins/",
            json=admin_data,
            timeout=5
        )
        
        if response.status_code == 200:
            admin = response.json()
            print(f"\n✓ Администратор успешно создан!")
            print(f"   ID: {admin['id']}")
            print(f"   Telegram ID: {admin['telegram_id']}")
            print(f"   Должность: {admin['role']}")
            print("\n" + "="*60)
            print("ГОТОВО!")
            print("="*60)
            return True
        else:
            print(f"✗ Ошибка создания администратора: {response.status_code}")
            print(f"Ответ сервера: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка при создании администратора: {e}")
        return False

if __name__ == "__main__":
    success = add_first_admin()
    sys.exit(0 if success else 1)

