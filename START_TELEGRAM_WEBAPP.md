# 🚀 Запуск для Telegram WebApp (Глобальный доступ)

## ⚡ Быстрый старт (3 шага)

### Шаг 1: Установите ngrok

1. Скачайте: https://ngrok.com/download
2. Распакуйте и добавьте в PATH
3. Зарегистрируйтесь и получите токен: https://dashboard.ngrok.com/get-started/your-authtoken
4. Авторизуйтесь: `ngrok config add-authtoken YOUR_TOKEN`

### Шаг 2: Запустите backend + ngrok

**Windows:**
```bash
cd backend
start_with_ngrok.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x start_with_ngrok.sh
./start_with_ngrok.sh
```

Или вручную:
```bash
# Терминал 1: Backend
cd backend
python run.py

# Терминал 2: ngrok
ngrok http 8000
```

### Шаг 3: Настройте React приложение

1. **Скопируйте HTTPS URL из ngrok**
   
   В окне ngrok вы увидите:
   ```
   Forwarding  https://abc123.ngrok.io -> http://localhost:8000
   ```
   
   Скопируйте: `https://abc123.ngrok.io`

2. **Создайте файл `miniapp/react-app/.env`:**
   ```
   REACT_APP_API_URL=https://abc123.ngrok.io
   ```
   
   ⚠️ Замените `abc123.ngrok.io` на ваш реальный URL!

3. **Перезапустите React приложение:**
   ```bash
   cd miniapp/react-app
   npm start
   ```

## ✅ Проверка

1. Откройте приложение в Telegram
2. Откройте DevTools (через меню Telegram)
3. В консоли должны быть:
   - `API Base URL configured: https://abc123.ngrok.io`
   - `API health check result: true 200`

## 🎉 Готово!

Теперь ваше приложение работает глобально в Telegram WebApp!

## 📝 Важные замечания

1. **ngrok URL меняется** при каждом перезапуске (в бесплатной версии)
   - Решение: Используйте зарегистрированный аккаунт ngrok
   - Или задеплойте на постоянный сервер

2. **Для production** лучше использовать:
   - VPS с доменом и SSL
   - Cloud платформы (Heroku, Railway, Render)

3. **CORS уже настроен** - backend разрешает запросы с любых источников

## 🔧 Альтернативы ngrok

- **localtunnel**: `npm install -g localtunnel && lt --port 8000`
- **Cloudflare Tunnel**: `cloudflared tunnel --url http://localhost:8000`
- **serveo**: `ssh -R 80:localhost:8000 serveo.net`

Подробнее: `TELEGRAM_WEBAPP_SETUP.md`

