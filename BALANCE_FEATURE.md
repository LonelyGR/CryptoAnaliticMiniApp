# Фича «Баланс» — настройка и проверка

## Переменные окружения

Добавьте в `.env` (см. `.env.example`):

```
DEPOSIT_ADDRESS=YOUR_USDT_TRC20_ADDRESS
DEPOSIT_NETWORK=USDT TRC20
CURRENCY=KZT
```

## Миграция БД

```bash
cd backend
python db_migrate.py
```

## Проверка локально

### 1. Запустить backend

```bash
cd backend
python run.py
# или: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Запустить frontend

```bash
cd miniapp/react-app
npm start
```

Для проверки в Telegram WebApp — настройте ngrok (см. TELEGRAM_WEBAPP_SETUP.md) и укажите `REACT_APP_API_URL` на HTTPS URL.

### 3. Endpoint'ы пользователя (требуют X-Telegram-Init-Data)

- `GET /me/balance` — баланс
- `GET /me/deposit-address` — адрес депозита и QR payload
- `POST /me/balance-requests` — создать заявку (body: `{ "tx_ref": "..." }`)

### 4. Админка

- Откройте `/admin` в браузере
- Раздел «Заявки на пополнение» — список, фильтр, approve/reject
- Раздел «Пользователи приложения» — список пользователей (User), профиль, блокировка, изменение баланса, ledger

### 5. Тесты

```bash
cd backend
python test_balance_manual.py
```

## Роли админов

Для доступа к разделу «Баланс» нужен scope `balance:view` (просмотр) и `balance:manage` (одобрение/отклонение, изменение баланса). Роль `admin` по умолчанию включает эти scope'ы.
