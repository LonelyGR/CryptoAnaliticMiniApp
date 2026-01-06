"""
Скрипт для добавления тестовых данных в базу данных
Использование: python add_sample_data.py
"""
import requests
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def add_sample_webinars():
    """Добавление тестовых вебинаров"""
    print("Добавление тестовых вебинаров...")
    
    webinars = [
        {
            "title": "Основы криптотрейдинга",
            "date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "time": "18:00",
            "duration": "2 часа",
            "speaker": "Иван Петров",
            "status": "upcoming",
            "description": "Изучите базовые принципы торговли криптовалютами и начните свой путь в трейдинге."
        },
        {
            "title": "Технический анализ криптовалют",
            "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time": "19:30",
            "duration": "2.5 часа",
            "speaker": "Мария Сидорова",
            "status": "upcoming",
            "description": "Глубокое погружение в технические индикаторы и паттерны для анализа рынка."
        },
        {
            "title": "DeFi и стейкинг",
            "date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "time": "17:00",
            "duration": "3 часа",
            "speaker": "Алексей Козлов",
            "status": "upcoming",
            "description": "Все о децентрализованных финансах и способах пассивного заработка на криптовалютах."
        },
        {
            "title": "Торговые стратегии для начинающих",
            "date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
            "time": "20:00",
            "duration": "1.5 часа",
            "speaker": "Дмитрий Волков",
            "status": "upcoming",
            "description": "Практические стратегии торговли для новичков в криптотрейдинге."
        }
    ]
    
    created = 0
    for webinar in webinars:
        try:
            response = requests.post(f"{BASE_URL}/webinars/", json=webinar, timeout=5)
            if response.status_code == 200:
                created_webinar = response.json()
                print(f"✓ Создан вебинар: {created_webinar['title']} (ID: {created_webinar['id']})")
                created += 1
            else:
                print(f"✗ Ошибка создания вебинара '{webinar['title']}': {response.status_code}")
        except Exception as e:
            print(f"✗ Ошибка при создании вебинара '{webinar['title']}': {e}")
    
    print(f"\nСоздано вебинаров: {created}/{len(webinars)}")
    return created

def check_server():
    """Проверка доступности сервера"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("="*60)
    print("ДОБАВЛЕНИЕ ТЕСТОВЫХ ДАННЫХ")
    print("="*60)
    
    if not check_server():
        print("✗ ОШИБКА: Сервер недоступен!")
        print("Запустите сервер: cd backend && python run.py")
        sys.exit(1)
    
    print("✓ Сервер доступен\n")
    
    webinars_count = add_sample_webinars()
    
    print("\n" + "="*60)
    print("ГОТОВО!")
    print("="*60)
    print(f"Добавлено вебинаров: {webinars_count}")
    print("\nТеперь вы можете:")
    print("1. Проверить вебинары через API: GET http://localhost:8000/webinars/")
    print("2. Открыть Swagger документацию: http://localhost:8000/docs")
    print("3. Запустить тесты: python test_api.py")

