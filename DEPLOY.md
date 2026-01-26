## Deploy (server) — docker-compose (prod, single domain + HTTPS)

### Что поднимается (prod)
- **caddy**: reverse-proxy + auto HTTPS (наружу только **80/443**)
- **frontend**: Nginx + статическая сборка React (внутренний порт 80)
- **backend**: FastAPI (gunicorn+uvicorn workers) (внутренний порт 8000)
- **bot**: long-polling Telegram bot (без портов)
- **reminders-worker**: loop-воркер, который вызывает `/reminders/check-and-send`

### 0) Требования
- Docker + Docker Compose на сервере

### 1) Подготовь env
Скопируй шаблон:

```bash
cp .env.example .env
```

Заполни минимум:
- `DOMAIN`
- `ACME_EMAIL`
- `CORS_ALLOW_ORIGINS` (твой `https://<DOMAIN>`)
- `TELEGRAM_BOT_TOKEN`
- `ADMIN_TELEGRAM_ID`

Если используешь реферальные ссылки:
- `TELEGRAM_BOT_USERNAME`

Если используешь NOWPayments:
- `NOWPAYMENTS_API_KEY`
- `NOWPAYMENTS_IPN_SECRET`
- `NOWPAYMENTS_IPN_CALLBACK_URL` (должен быть публичным URL)

### 2) Запуск

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Проверки:
- frontend: `https://<DOMAIN>/`
- API: `https://<DOMAIN>/api/`

### Если Docker не установлен
На Windows/Linux сервере сначала поставь Docker (и Compose). Если деплоишь без Docker:
- backend: см. `backend/start_prod.sh`
- frontend: собери `npm run build` и отдай через nginx (или любой static server), проксируя `/api` на backend

### 3) Где лежит база
По умолчанию используется SQLite в volume `backend-data`:
- внутри контейнера: `/data/db.sqlite3`

### 4) Переключение на Postgres (по желанию)
Можно поменять `DATABASE_URL` в `docker-compose.yml` на Postgres и добавить сервис postgres.

### 5) Рекомендации для продакшена
- **Порт 8000 наружу не открывать** — в `docker-compose.prod.yml` его нет.
- **CORS**: держать только `https://<DOMAIN>`.
- Не хранить `.env` в git, держать только `.env.example`.
