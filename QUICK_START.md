# Быстрый старт

## Запуск Backend сервера

1. Откройте терминал в папке `backend`
2. Активируйте виртуальное окружение:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```
3. Установите зависимости (если еще не установлены):
   ```bash
   pip install -r requirements.txt
   ```
4. Запустите сервер:
   ```bash
   python run.py
   ```
   
   Или используйте `start.bat` (Windows) или `start.sh` (Linux/Mac)

Сервер запустится на http://localhost:8000

## Запуск Miniapp

1. Откройте новый терминал в папке `miniapp/react-app`
2. Установите зависимости (если еще не установлены):
   ```bash
   npm install
   ```
3. Запустите приложение:
   ```bash
   npm start
   ```

Приложение откроется в браузере на http://localhost:3000

## Добавление тестовых вебинаров

После запуска backend сервера, вы можете добавить вебинары через API:

### Через браузер (Swagger UI)
Откройте http://localhost:8000/docs и используйте интерфейс для создания вебинаров

### Через curl (пример)
```bash
curl -X POST "http://localhost:8000/webinars/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Основы криптотрейдинга",
    "date": "2024-12-20",
    "time": "18:00",
    "duration": "2 часа",
    "speaker": "Иван Петров",
    "status": "upcoming",
    "description": "Изучите базовые принципы торговли криптовалютами"
  }'
```

### Через Python скрипт
Создайте файл `backend/add_sample_webinars.py`:

```python
import requests

webinars = [
    {
        "title": "Основы криптотрейдинга",
        "date": "2024-12-20",
        "time": "18:00",
        "duration": "2 часа",
        "speaker": "Иван Петров",
        "status": "upcoming",
        "description": "Изучите базовые принципы торговли криптовалютами и начните свой путь в трейдинге."
    },
    {
        "title": "Технический анализ криптовалют",
        "date": "2024-12-25",
        "time": "19:30",
        "duration": "2.5 часа",
        "speaker": "Мария Сидорова",
        "status": "upcoming",
        "description": "Глубокое погружение в технические индикаторы и паттерны для анализа рынка."
    },
    {
        "title": "DeFi и стейкинг",
        "date": "2025-01-05",
        "time": "17:00",
        "duration": "3 часа",
        "speaker": "Алексей Козлов",
        "status": "upcoming",
        "description": "Все о децентрализованных финансах и способах пассивного заработка на криптовалютах."
    }
]

for webinar in webinars:
    response = requests.post("http://localhost:8000/webinars/", json=webinar)
    print(f"Created: {webinar['title']} - {response.status_code}")
```

Запустите:
```bash
python add_sample_webinars.py
```

## Проверка работы

1. Backend должен отвечать на http://localhost:8000/ с сообщением `{"Status": "OK", "message": "Crypto Analytics API is running"}`
2. Miniapp должна подключаться к backend и загружать данные
3. Если сервер недоступен, miniapp покажет предупреждение, но продолжит работать

## Структура базы данных

База данных SQLite создается автоматически в `backend/db.sqlite3` при первом запуске.

Таблицы:
- `users` - пользователи
- `webinars` - вебинары
- `bookings` - записи на вебинары и консультации

