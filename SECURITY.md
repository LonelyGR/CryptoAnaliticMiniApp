## Security pack (максимум защит)

Этот репозиторий содержит **реально включённые** защиты (Caddy/Compose/backend) и **шаблоны** для продакшн‑технологий, которые могут быть подключены “снаружи” (WAF/IDS/SIEM), даже если сейчас их нет.

### 1) Что уже включено в этом репо
- **Edge hardening (Caddy)**: `Caddyfile`
  - **убран `Server` header** (и Caddy, и upstream)
  - **раздельные политики** для:
    - **frontend**: CSP с `frame-ancestors` под Telegram Mini App
    - **/admin***: `X-Frame-Options: DENY` + CSP `frame-ancestors 'none'`
    - **/api/***: `Cache-Control: no-store`, `X-Robots-Tag: noindex, nofollow`
  - **anti-scan**: быстрые 404 на типовые “сканерные” пути (`/wp-admin`, `/.env`, `/.git` и т.д.)
  - **request body limits**: глобально 5MB, для `/api` 2MB
  - **таймауты** на уровне серверов
  - **structured access logs (JSON)** в volume `caddy_logs`

- **Container hardening (prod compose)**: `docker-compose.prod.yml`
  - `security_opt: no-new-privileges:true`
  - `read_only: true` для edge + frontend (и tmpfs для runtime‑папок)
  - отдельный volume `caddy_logs` для логов edge

- **Backend hardening**: `backend/app/main.py`
  - **CORS больше не падает в `*`** если забыли env (использует `DOMAIN`, либо fail-closed)
  - **TrustedHostMiddleware** (если `DOMAIN` задан)
  - базовые security headers на ответах API

### 2) Что намеренно НЕ включено “автоматом”
Некоторые защиты требуют внешней инфраструктуры/учёток/изменений на сервере. Здесь — **шаблоны**, но они не активируются по умолчанию (чтобы не сломать доступ/деплой).

### 3) Рекомендованные “внешние” уровни защиты (добавляются поверх)

#### 3.1 WAF / Bot Management (Cloudflare — рекомендую)
- **Зачем**: снижает скан/бот‑трафик, даёт rate limiting без плагинов Caddy, защищает от DDoS.
- **Что включить**:
  - WAF managed rules
  - Bot Fight Mode / Super Bot Fight Mode (если есть)
  - Rate limiting на:
    - `/api/*` (например 60 req/min per IP)
    - `/admin*` (например 20 req/min per IP)
  - “Under Attack” режим при инциденте
- **Проверка**: убедиться, что Telegram WebView не режется (User-Agent/ASNs), и что `/api` доступен.

#### 3.2 CrowdSec (поведенческий антибот) — шаблон
Ставится на сервер/в docker и банит IP через firewall/блокировки на edge.

Файлы-шаблоны (создай у себя на сервере):
- `/etc/crowdsec/acquis.yaml` — сбор логов Caddy из `caddy_logs`
- парсер для JSON‑логов Caddy
- сценарии/коллекции: `crowdsecurity/http-cve`, `crowdsecurity/sshd`, `crowdsecurity/nginx` (для веб‑паттернов)

#### 3.3 Fail2ban (базовый анти‑брут/анти‑скан) — шаблон
- **Источники**: SSH + web access logs
- **Триггеры**:
  - много 404/403/401 за короткое время
  - попытки доступа к `/.env`, `/.git`, `/wp-admin`

#### 3.4 IDS/EDR (если хочется “по максимуму”)
- **Wazuh/OSSEC**: агент на сервере, auditd, алерты на изменения файлов, подозрительные процессы
- **Falco** (для контейнеров): алерты на необычные syscalls/exec внутри контейнеров

#### 3.5 SIEM / лог‑агрегация
- Loki + Promtail + Grafana (быстро)
- ELK / OpenSearch (тяжелее)
- Отдельно: алерты по 3xx/4xx/5xx, скачку 404 на “сканерные” пути

### 4) Telegram Mini App особенности (чтобы “защиты” не ломали запуск)
- **Не ставить** `X-Frame-Options: DENY` на фронт (мы ставим DENY только на `/admin*`)
- **CSP `frame-ancestors`** должен включать Telegram домены (`web.telegram.org`, `*.telegram.org`, `t.me`)
- **Смешанный контент**: запрещён, только HTTPS
- **Редиректы**: никаких кросс-доменных цепочек и петель

### 5) Safe Browsing “hygiene”
- Убрать внешние “необъяснимые” CDN/скрипты (в этом репо уже убраны `unpkg` и внешний QR API)
- Держать выдачу детерминированной (без клоакинга по UA/IP)
- Иметь логи и подтверждение исправлений перед review

