# Быстрый старт для тестирования

## 0. Настройка окружения (первый раз)

Если виртуальное окружение еще не создано:

**Windows:**
```bash
cd backend
setup.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

## 1. Запустите сервер

**Windows:**
```bash
cd backend
start.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x start.sh
./start.sh
```

Или вручную:
```bash
cd backend
venv\Scripts\activate  # Windows
# или
source venv/bin/activate  # Linux/Mac
python run.py
```

Должно появиться: `Uvicorn running on http://0.0.0.0:8000`

## 2. Быстрая проверка (30 секунд)

В **новом терминале**:

```bash
cd backend
python test_api_simple.py
```

Если все тесты прошли - API работает! ✓

## 3. Полное тестирование (2 минуты)

```bash
python test_api.py
```

Этот скрипт проверит:
- ✓ Подключение к серверу
- ✓ CORS настройки
- ✓ Создание пользователя
- ✓ Создание вебинара
- ✓ Создание записи
- ✓ Получение данных

## 4. Добавление тестовых данных

```bash
python add_sample_data.py
```

Добавит 4 тестовых вебинара в базу данных.

## 5. Тестирование в браузере

Откройте: http://localhost:8000/docs

Вы увидите интерактивную документацию Swagger, где можно:
- Просмотреть все эндпоинты
- Тестировать API прямо в браузере
- Видеть примеры запросов и ответов

## Готово!

Теперь API полностью протестирован и готов к работе с фронтендом или деплою на сервер.

