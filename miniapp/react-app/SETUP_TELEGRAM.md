# Настройка для Telegram WebApp

## Быстрая настройка

### 1. Запустите backend с ngrok

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

### 2. Скопируйте HTTPS URL из ngrok

В окне ngrok вы увидите что-то вроде:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

Скопируйте URL: `https://abc123.ngrok.io`

### 3. Обновите .env файл

Создайте или обновите `miniapp/react-app/.env`:

```
REACT_APP_API_URL=https://abc123.ngrok.io
```

**Важно:** Замените `abc123.ngrok.io` на ваш реальный ngrok URL!

### 4. Перезапустите React приложение

```bash
cd miniapp/react-app
npm start
```

### 5. Проверьте в Telegram

1. Откройте ваше приложение в Telegram
2. Откройте DevTools (через меню Telegram)
3. Проверьте консоль - должны быть сообщения об успешном подключении

## Альтернативы ngrok

### localtunnel

```bash
npm install -g localtunnel
lt --port 8000
```

### Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:8000
```

## Production

Для production задеплойте backend на сервер с HTTPS и обновите `.env`:

```
REACT_APP_API_URL=https://api.yourdomain.com
```

