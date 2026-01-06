# Руководство по тестированию API

Это руководство поможет вам протестировать backend API без необходимости запуска фронтенда.

## Быстрая проверка

### 1. Простая проверка (30 секунд)

```bash
cd backend
python test_api_simple.py
```

Этот скрипт быстро проверит все основные эндпоинты.

### 2. Полное тестирование (2-3 минуты)

```bash
cd backend
python test_api.py
```

Этот скрипт выполнит полный набор тестов:
- ✓ Проверка подключения к серверу
- ✓ Проверка CORS
- ✓ Создание пользователя
- ✓ Получение пользователя
- ✓ Создание вебинара
- ✓ Получение списка вебинаров
- ✓ Создание записи на вебинар
- ✓ Получение записей пользователя

### 3. Добавление тестовых данных

```bash
cd backend
python add_sample_data.py
```

Этот скрипт добавит 4 тестовых вебинара в базу данных.

## Тестирование через браузер

### Swagger UI (Интерактивная документация)

1. Запустите сервер: `python run.py`
2. Откройте в браузере: http://localhost:8000/docs
3. Вы можете тестировать все эндпоинты прямо в браузере!

### ReDoc (Альтернативная документация)

Откройте: http://localhost:8000/redoc

## Тестирование через curl

### Проверка основного эндпоинта
```bash
curl http://localhost:8000/
```

### Получение списка вебинаров
```bash
curl http://localhost:8000/webinars/
```

### Создание вебинара
```bash
curl -X POST "http://localhost:8000/webinars/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Тестовый вебинар",
    "date": "2024-12-20",
    "time": "18:00",
    "duration": "2 часа",
    "speaker": "Тестовый Спикер",
    "status": "upcoming",
    "description": "Описание вебинара"
  }'
```

### Создание пользователя
```bash
curl -X POST "http://localhost:8000/users/telegram/123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "first_name": "Тестовый",
    "last_name": "Пользователь"
  }'
```

### Получение пользователя
```bash
curl http://localhost:8000/users/telegram/123456789
```

### Создание записи на вебинар
```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "webinar_id": 1,
    "type": "webinar",
    "date": "2024-12-20",
    "status": "active"
  }'
```

## Тестирование через Python requests

Создайте файл `test_custom.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

# Получить вебинары
response = requests.get(f"{BASE_URL}/webinars/")
print(response.json())

# Создать вебинар
webinar = {
    "title": "Мой тестовый вебинар",
    "date": "2024-12-25",
    "time": "19:00",
    "duration": "2 часа",
    "speaker": "Я",
    "status": "upcoming",
    "description": "Описание"
}
response = requests.post(f"{BASE_URL}/webinars/", json=webinar)
print(response.json())
```

Запустите: `python test_custom.py`

## Проверка перед деплоем

### Чеклист:

- [ ] Сервер запускается без ошибок
- [ ] Все эндпоинты отвечают (запустите `test_api.py`)
- [ ] CORS настроен правильно
- [ ] База данных создается автоматически
- [ ] Можно создавать пользователей
- [ ] Можно создавать вебинары
- [ ] Можно создавать записи
- [ ] Swagger документация доступна

### Команда для полной проверки:

```bash
cd backend
python test_api_simple.py && python test_api.py && python add_sample_data.py
```

Если все три скрипта выполнились успешно - API готов к работе!

## Решение проблем

### Сервер не запускается

1. Проверьте, что порт 8000 свободен:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. Проверьте зависимости:
   ```bash
   pip install -r requirements.txt
   ```

### Ошибки при тестировании

1. Убедитесь, что сервер запущен: `python run.py`
2. Проверьте логи сервера на наличие ошибок
3. Убедитесь, что база данных создана (файл `db.sqlite3` должен существовать)

### База данных не создается

1. Убедитесь, что у вас есть права на запись в папку `backend`
2. Проверьте, что SQLAlchemy установлен: `pip install sqlalchemy`

## Автоматическое тестирование

Для CI/CD можно использовать:

```bash
# В скрипте деплоя
cd backend
python test_api_simple.py || exit 1
```

Это вернет код ошибки, если тесты не пройдены.

