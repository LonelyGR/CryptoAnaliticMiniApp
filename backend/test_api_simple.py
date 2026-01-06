"""
Простой скрипт для быстрой проверки работы API
Использование: python test_api_simple.py
"""
import requests

BASE_URL = "http://localhost:8000"

def quick_test():
    """Быстрая проверка основных эндпоинтов"""
    print("Быстрая проверка API...\n")
    
    endpoints = [
        ("GET", "/", "Основной эндпоинт"),
        ("GET", "/webinars/", "Список вебинаров"),
        ("GET", "/users/", "Список пользователей"),
        ("GET", "/bookings/", "Список записей"),
    ]
    
    all_ok = True
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=3)
            
            if response.status_code == 200:
                print(f"✓ {name}: OK ({response.status_code})")
            else:
                print(f"✗ {name}: Ошибка ({response.status_code})")
                all_ok = False
        except requests.exceptions.ConnectionError:
            print(f"✗ {name}: Сервер недоступен!")
            all_ok = False
        except Exception as e:
            print(f"✗ {name}: {e}")
            all_ok = False
    
    print()
    if all_ok:
        print("✓ Все эндпоинты работают!")
        print(f"Документация: {BASE_URL}/docs")
    else:
        print("✗ Есть проблемы. Проверьте логи выше.")
        print("Убедитесь, что сервер запущен: cd backend && python run.py")
    
    return all_ok

if __name__ == "__main__":
    import sys
    success = quick_test()
    sys.exit(0 if success else 1)

