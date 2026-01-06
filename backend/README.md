# Crypto Analytics Backend API

FastAPI backend для мини-приложения Crypto Analytics.

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск сервера

```bash
python run.py
```

Или с помощью uvicorn напрямую:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: http://localhost:8000

## API Endpoints

### Пользователи
- `GET /users/` - Получить список пользователей
- `GET /users/{user_id}` - Получить пользователя по ID
- `GET /users/telegram/{telegram_id}` - Получить пользователя по Telegram ID
- `POST /users/` - Создать пользователя
- `POST /users/telegram/{telegram_id}` - Создать/обновить пользователя по Telegram ID

### Вебинары
- `GET /webinars/` - Получить список вебинаров
- `GET /webinars/{webinar_id}` - Получить вебинар по ID
- `POST /webinars/` - Создать вебинар

### Записи
- `GET /bookings/` - Получить список записей
- `GET /bookings/user/{user_id}` - Получить записи пользователя по user_id
- `GET /bookings/telegram/{telegram_id}` - Получить записи пользователя по telegram_id
- `GET /bookings/{booking_id}` - Получить запись по ID
- `POST /bookings/` - Создать запись

## База данных

Используется SQLite база данных `db.sqlite3`. Таблицы создаются автоматически при первом запуске.

## Тестирование API

### Быстрая проверка
```bash
python test_api_simple.py
```

### Полное тестирование
```bash
python test_api.py
```

### Добавление тестовых данных
```bash
python add_sample_data.py
```

Подробнее см. [TESTING.md](TESTING.md)

## Документация API

После запуска сервера документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs (интерактивное тестирование)
- ReDoc: http://localhost:8000/redoc

