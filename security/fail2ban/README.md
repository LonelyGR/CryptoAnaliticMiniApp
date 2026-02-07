## Fail2ban (шаблон)

Fail2ban работает на **хосте** (не внутри compose этого репо) и банит IP через firewall.

### Что баним
- массовые запросы к “сканерным” путям (`/.env`, `/.git`, `/wp-admin` и т.д.)
- (опционально) брутфорс/подбор на `/admin*` и чувствительных API‑ручках

### Источник логов
Edge Caddy пишет JSON‑логи в volume `caddy_logs` → на сервере это будет путь, где примонтирован volume.

### Дальше
См. `security/fail2ban/jail.local` и `security/fail2ban/filter.d/caddy-scan.conf`.

