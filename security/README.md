## security/ — опциональные “внешние” защиты

Эта папка содержит **шаблоны** для прод‑защит, которые обычно подключаются поверх приложения:
- **Observability**: Loki + Grafana + Promtail (сбор JSON‑логов Caddy).
- **Anti-bot / Anti-scan**: CrowdSec и/или Fail2ban (по логам).
- **Rate limiting / WAF**: рекомендации под Cloudflare (без привязки к провайдеру).

### Быстрый старт: observability (логи + дашборды)
1) Запусти:
```bash
docker compose -f docker-compose.observability.yml up -d
```
2) Открой Grafana (по умолчанию `http://localhost:3000`) и добавь datasource Loki (уже провиженится).

### Anti-scan: CrowdSec / Fail2ban
- CrowdSec и Fail2ban **не включены автоматически**: сначала нужно выбрать стратегию (iptables ban / reverse-proxy bouncer / WAF).
- Шаблоны конфигов лежат в `security/crowdsec/` и `security/fail2ban/`.

### Важно про Telegram Mini App
Защиты **не должны** ломать:
- `frame-ancestors` (CSP) для фронта
- HTTPS-only (никакого mixed content)
- редиректы (без петель и кросс-доменных цепочек)

