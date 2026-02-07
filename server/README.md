## Server runbook (prod)

Ниже — минимальный, но “боевой” способ поднять проект на сервере через Docker Compose.

### 0) Предусловия (сервер)
- Linux VPS
- DNS `A` для `cryptosensei.info` → IP сервера
- Открыты наружу только **80/443** (и **22** ограниченно)

### 1) Установка Docker/Compose
Поставь Docker + Compose по официальной инструкции под твой дистрибутив.

Проверка:
```bash
docker --version
docker compose version
```

### 2) Клонирование репо и env
```bash
git clone <YOUR_REPO_URL> CryptoAnaliticMiniApp
cd CryptoAnaliticMiniApp
cp .env.example .env
```

Обязательно заполнить в `.env`:
- `DOMAIN=cryptosensei.info`
- `ACME_EMAIL=...`
- `TELEGRAM_BOT_TOKEN=...`
- `ADMIN_PANEL_SECRET=...` (рандом)
- `INTERNAL_API_KEY=...` (рандом)
- `ADMIN_TELEGRAM_ID=...`

### 3) Первый запуск (prod)
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Проверки:
```bash
curl -sSIL http://cryptosensei.info/
curl -sSI  https://cryptosensei.info/ | grep -iE 'content-security-policy|strict-transport-security|server:'
curl -sSI  https://cryptosensei.info/api/
```

### 4) Обновление (redeploy)
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker image prune -f
```

### 5) Логи
Edge логи (Caddy) пишутся в docker volume `caddy_logs`.

Просмотр последних логов сервисов:
```bash
docker compose -f docker-compose.prod.yml logs -n 200 --no-log-prefix caddy
docker compose -f docker-compose.prod.yml logs -n 200 --no-log-prefix backend
```

### 6) Observability (опционально)
Если хочешь Loki+Grafana:
```bash
docker compose -f docker-compose.observability.yml up -d
```

Grafana по умолчанию: `http://<SERVER_IP>:3000` (закрой firewall’ом или вынеси за VPN/SSO).

### 7) Firewall (шаблон)
Открыть: 80/443, 22 (ограничить по IP).

### 8) Telegram Mini App важное
- На фронте нельзя ставить `X-Frame-Options: DENY`. В этом проекте DENY применяется **только** на `/admin*`.
- CSP `frame-ancestors` уже настроен для Telegram Web.

