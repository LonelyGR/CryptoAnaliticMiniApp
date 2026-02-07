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

### Runbook
Подробная инструкция “как поднять на сервере” (firewall/обновления/логи):
- `server/README.md`

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
- **CORS**: держать только `https://<DOMAIN>` (если не задан `CORS_ALLOW_ORIGINS`, backend возьмёт его из `DOMAIN`).
- Не хранить `.env` в git, держать только `.env.example`.

### 6) Security sanity-check (быстро, перед продом и перед review)
Проверки с локальной машины:

```bash
# редирект http -> https
curl -sSIL http://<DOMAIN>/

# один Server header (или вообще без него) + security headers
curl -sSI https://<DOMAIN>/ | rg -i "^server:|content-security-policy|strict-transport-security|permissions-policy|referrer-policy|x-content-type-options"

# API отвечает через прокси (и не открыта наружу на :8000)
curl -sSI https://<DOMAIN>/api/

# PDF worker (если используется экран презентации)
curl -sSI https://<DOMAIN>/pdf.worker.min.mjs
```

Если пользователи открывают Mini App в Telegram Web:
- убедись, что нет `X-Frame-Options: DENY` и что CSP содержит `frame-ancestors` совместимый с Telegram.

### 7) Observability (опционально, “по максимуму”)
Если хочешь логи/алерты/поиск аномалий:
- см. `security/README.md`
- подними Loki+Grafana+Promtail: `docker compose -f docker-compose.observability.yml up -d`

