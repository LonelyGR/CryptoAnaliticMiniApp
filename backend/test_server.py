"""
Скрипт для проверки работы сервера
Запустите этот скрипт чтобы убедиться, что сервер работает правильно
"""
import requests
import sys

def test_server():
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("Тестирование сервера")
    print("=" * 50)
    
    # Тест 1: Проверка основного эндпоинта
    print("\n1. Проверка основного эндпоинта (GET /)...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
        if response.status_code == 200:
            print("   ✓ Сервер работает!")
        else:
            print("   ✗ Сервер вернул ошибку")
            return False
    except requests.exceptions.ConnectionError:
        print("   ✗ ОШИБКА: Не удалось подключиться к серверу")
        print("   Убедитесь, что сервер запущен на http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("   ✗ ОШИБКА: Превышено время ожидания")
        return False
    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
        return False
    
    # Тест 2: Проверка CORS
    print("\n2. Проверка CORS заголовков...")
    try:
        response = requests.options(f"{base_url}/", timeout=5)
        print(f"   Статус OPTIONS: {response.status_code}")
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        print(f"   CORS заголовки: {cors_headers}")
        if cors_headers['Access-Control-Allow-Origin']:
            print("   ✓ CORS настроен")
        else:
            print("   ⚠ CORS заголовки не найдены (может быть проблемой)")
    except Exception as e:
        print(f"   ⚠ Не удалось проверить CORS: {e}")
    
    # Тест 3: Проверка эндпоинта вебинаров
    print("\n3. Проверка эндпоинта вебинаров (GET /webinars/)...")
    try:
        response = requests.get(f"{base_url}/webinars/", timeout=5)
        print(f"   Статус: {response.status_code}")
        webinars = response.json()
        print(f"   Количество вебинаров: {len(webinars)}")
        if response.status_code == 200:
            print("   ✓ Эндпоинт вебинаров работает!")
        else:
            print("   ✗ Эндпоинт вернул ошибку")
    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
    
    # Тест 4: Проверка эндпоинта пользователей
    print("\n4. Проверка эндпоинта пользователей (GET /users/)...")
    try:
        response = requests.get(f"{base_url}/users/", timeout=5)
        print(f"   Статус: {response.status_code}")
        users = response.json()
        print(f"   Количество пользователей: {len(users)}")
        if response.status_code == 200:
            print("   ✓ Эндпоинт пользователей работает!")
        else:
            print("   ✗ Эндпоинт вернул ошибку")
    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
    
    print("\n" + "=" * 50)
    print("Тестирование завершено")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)

