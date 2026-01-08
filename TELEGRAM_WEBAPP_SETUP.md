# Настройка для Telegram WebApp (Глобальный доступ)

## Проблема

Telegram WebApp требует HTTPS для работы с внешними API. `localhost` не будет работать в Telegram.

## Решение: Использование туннеля

### Вариант 1: ngrok (Рекомендуется)

#### Шаг 1: Установите ngrok

1. Скачайте с https://ngrok.com/download
2. Зарегистрируйтесь и получите бесплатный токен
3. Распакуйте и добавьте в PATH
4. Авторизуйтесь: `ngrok config add-authtoken YOUR_TOKEN`

#### Шаг 2: Запустите backend

```bash
cd backend
python run.py
```

#### Шаг 3: Запустите ngrok (в новом терминале)

```bash
ngrok http 8000
```

Вы увидите что-то вроде:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

#### Шаг 4: Настройте React приложение

Создайте файл `miniapp/react-app/.env`:

```
REACT_APP_API_URL=https://abc123.ngrok.io
```

**Важно:** Замените `abc123.ngrok.io` на ваш реальный ngrok URL!

#### Шаг 5: Перезапустите React приложение

```bash
cd miniapp/react-app
npm start
```

### Вариант 2: localtunnel (Альтернатива)

#### Установка:
```bash
npm install -g localtunnel
```

#### Запуск:
```bash
lt --port 8000
```

Вы получите URL типа: `https://random-name.loca.lt`

Обновите `.env` с этим URL.

### Вариант 3: Cloudflare Tunnel (Бесплатно, без ограничений)

1. Установите cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
2. Запустите: `cloudflared tunnel --url http://localhost:8000`
3. Используйте полученный URL в `.env`

## Автоматическая настройка

Используйте скрипт:

```bash
cd backend
python setup_ngrok.py
```

Скрипт поможет настроить ngrok и покажет, что нужно добавить в `.env`.

## Production деплой

Для production используйте:

### Вариант 1: VPS сервер

1. Задеплойте backend на VPS (например, через Docker)
2. Настройте домен с SSL сертификатом (Let's Encrypt)
3. Обновите `.env`:
   ```
   REACT_APP_API_URL=https://api.yourdomain.com
   ```

### Вариант 2: Cloud платформы

- **Heroku**: Бесплатный хостинг с HTTPS
- **Railway**: Простой деплой
- **Render**: Бесплатный хостинг
- **Fly.io**: Быстрый деплой

## Проверка работы

1. Запустите backend
2. Запустите туннель (ngrok/localtunnel)
3. Обновите `.env` с HTTPS URL
4. Перезапустите React приложение
5. Откройте приложение в Telegram
6. Проверьте консоль браузера (в Telegram WebApp):
   - Откройте DevTools через меню Telegram
   - Должны быть сообщения об успешном подключении

## Важные замечания

1. **HTTPS обязателен** - Telegram требует HTTPS для внешних запросов
2. **CORS настроен** - Backend уже настроен с `allow_origins=["*"]`
3. **Бесплатные туннели** имеют ограничения:
   - ngrok: ограничение по времени в бесплатной версии
   - localtunnel: может быть нестабильным
4. **Для production** лучше использовать реальный сервер с доменом

## Быстрая команда для ngrok

Создайте файл `backend/start_with_ngrok.bat` (Windows):

```batch
@echo off
echo Запуск backend и ngrok...
start cmd /k "python run.py"
timeout /t 3
start cmd /k "ngrok http 8000"
echo Backend и ngrok запущены!
echo Скопируйте HTTPS URL из ngrok и обновите .env файл
pause
```

Или `backend/start_with_ngrok.sh` (Linux/Mac):

```bash
#!/bin/bash
python run.py &
sleep 3
ngrok http 8000 &
echo "Backend и ngrok запущены!"
echo "Скопируйте HTTPS URL из ngrok и обновите .env файл"
```

## Пример .env файла

```
# Для разработки с ngrok
REACT_APP_API_URL=https://abc123.ngrok.io

# Для production
# REACT_APP_API_URL=https://api.yourdomain.com
```

## Решение проблем

### Проблема: "Mixed Content" ошибка

**Причина:** Приложение пытается использовать HTTP вместо HTTPS

**Решение:** Убедитесь, что в `.env` указан HTTPS URL

### Проблема: CORS ошибка в Telegram

**Причина:** Backend не настроен правильно

**Решение:** Проверьте `backend/app/main.py` - должно быть `allow_origins=["*"]`

### Проблема: ngrok URL меняется каждый раз

**Решение:** 
- Используйте ngrok с зарегистрированным аккаунтом
- Или используйте фиксированный домен (платная версия ngrok)
- Или задеплойте на постоянный сервер

