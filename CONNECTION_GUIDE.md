# Руководство по подключению Frontend к Backend

## Быстрое подключение

### 1. Убедитесь, что backend запущен

```bash
cd backend
python run.py
```

Сервер должен быть доступен по адресу: http://localhost:8000

Проверьте в браузере: http://localhost:8000/docs

### 2. Настройте URL API в React приложении

Файл `.env` уже создан в `miniapp/react-app/.env`:

```
REACT_APP_API_URL=http://localhost:8000
```

**Важно:** Если вы изменили `.env`, перезапустите React приложение!

### 3. Запустите React приложение

```bash
cd miniapp/react-app
npm start
```

Приложение откроется на http://localhost:3000

### 4. Проверьте подключение

1. Откройте консоль браузера (F12)
2. Найдите сообщения:
   - `API Base URL configured: http://localhost:8000`
   - `API health check result: true 200`

Если видите эти сообщения - подключение работает!

## Настройка для разных окружений

### Локальная разработка

`.env` файл:
```
REACT_APP_API_URL=http://localhost:8000
```

### Production (если сервер на другом хосте)

`.env` файл:
```
REACT_APP_API_URL=https://your-server.com
```

Или если сервер на другом порту:
```
REACT_APP_API_URL=http://192.168.1.100:8000
```

### Telegram WebApp (через туннель)

Если приложение запущено в Telegram, `localhost` не будет работать. Используйте туннель:

1. Установите ngrok: https://ngrok.com/
2. Запустите backend
3. В другом терминале:
   ```bash
   ngrok http 8000
   ```
4. Скопируйте HTTPS URL (например: `https://abc123.ngrok.io`)
5. Обновите `.env`:
   ```
   REACT_APP_API_URL=https://abc123.ngrok.io
   ```
6. Перезапустите React приложение

## Проверка подключения

### Через браузер

1. Откройте http://localhost:3000
2. Откройте DevTools (F12) → Console
3. Должны быть сообщения:
   - `API Base URL configured: http://localhost:8000`
   - `Checking API health at: http://localhost:8000`
   - `API health check result: true 200`

### Через тесты

```bash
cd backend
python test_api_simple.py
```

Все тесты должны пройти успешно.

## Решение проблем

### Проблема: "Failed to fetch" или "NetworkError"

**Причина:** Сервер не запущен или недоступен

**Решение:**
1. Проверьте, что backend запущен: `cd backend && python run.py`
2. Откройте http://localhost:8000 в браузере
3. Проверьте файрвол/антивирус

### Проблема: CORS ошибка

**Причина:** CORS не настроен правильно

**Решение:**
- Backend уже настроен с `allow_origins=["*"]`
- Если проблема сохраняется, проверьте `backend/app/main.py`

### Проблема: API URL неправильный

**Причина:** `.env` файл не загружен или URL неправильный

**Решение:**
1. Проверьте файл `miniapp/react-app/.env`
2. Убедитесь, что URL правильный: `http://localhost:8000`
3. Перезапустите React приложение после изменения `.env`

### Проблема: В Telegram WebApp не работает

**Причина:** `localhost` не работает в Telegram

**Решение:**
- Используйте ngrok или другой туннель
- Или используйте IP адрес вашего компьютера вместо localhost

## Структура подключения

```
React App (localhost:3000)
    ↓ HTTP запросы
    ↓
Backend API (localhost:8000)
    ↓
SQLite Database
```

## API Endpoints используемые фронтендом

- `GET /` - проверка доступности
- `GET /users/telegram/{telegram_id}` - получить пользователя
- `POST /users/telegram/{telegram_id}` - создать/обновить пользователя
- `GET /webinars/` - получить список вебинаров
- `GET /bookings/telegram/{telegram_id}` - получить записи пользователя
- `POST /bookings/` - создать запись

Все эти эндпоинты уже настроены и работают!

