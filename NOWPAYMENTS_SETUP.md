# NOWPayments интеграция — карта файлов

Этот документ описывает, какие файлы отвечают за приём крипто‑платежей через NOWPayments, как устроен поток и где править поведение.

## Основной поток оплаты

1. Пользователь нажимает «Оплатить» в вебинарах.
2. Фронт вызывает бэкенд `POST /payments/create`.
3. Бэкенд создаёт платёж в NOWPayments (`/v1/payment`) и сохраняет `payment_id` в БД (если `order_id` вида `booking-123`).
4. Фронт получает `payment_id`, `pay_address`, `pay_amount` и показывает инструкции/QR.
5. Фронт каждые 10 секунд опрашивает `GET /payments/payment/{payment_id}` (полный объект NOWPayments).
6. IPN (webhook) от NOWPayments (`POST /payments/ipn`) подтверждает оплату и обновляет Booking/Payment в БД.

---

## Backend

### `backend/app/routers/nowpayments.py`
**Что делает:**
- Эндпоинты:
  - `GET /payments/currencies`
  - `POST /payments/create`
  - `GET /payments/status/{payment_id}`
  - `GET /payments/payment/{payment_id}`
  - `POST /payments/ipn`
- Работает с NOWPayments API через `requests`.
- Проверяет подпись IPN (`X-NOWPayments-Sig`) и пишет событие IPN в БД.
- Обновляет платеж/бронь в БД по статусам NOWPayments (выдача доступа только по `finished`).

**Ключевые места:**
- Формирование invoice и payment.
- Присвоение `invoice_url` и `payment_link`.
- Сохранение `payment_metadata` в БД.
- Маппинг статусов NOWPayments → `payments.status` и `bookings.payment_status`.

---

### `backend/app/schemas/nowpayments.py`
**Что делает:**
- Pydantic‑модели для запросов/ответов бекенда по NOWPayments.

---

### `backend/app/utils/security.py`
**Что делает:**
- Проверка подписи webhook:
  - сортировка ключей
  - `json.dumps(..., sort_keys=True, separators=(',', ':'))`
  - `hmac.new(secret, ..., hashlib.sha512)`

---

### `backend/app/main.py`
**Что делает:**
- Подключает роут `nowpayments.router`.

---

### `.env (root проекта)`
**Что нужно:**
- `NOWPAYMENTS_API_KEY=...`
- `NOWPAYMENTS_IPN_SECRET=...`
- `NOWPAYMENTS_IPN_CALLBACK_URL=https://<домен>/api/payments/ipn`

---

## Frontend

### `miniapp/react-app/src/screens/Bookings.js`
**Что делает:**
- Кнопка «Оплатить» открывает модалку с `PaymentFlow`.
- Передаёт:
  - `orderId` (booking)
  - `amount` (цена в USDT)
  - `priceCurrency` = `usd`
  - `fixedPayCurrency` = `usdttrc20`

---

### `miniapp/react-app/src/components/PaymentFlow.js`
**Что делает:**
- Создаёт платёж через `POST /payments/create`.
- Поллит `GET /payments/payment/{payment_id}`.
- Показывает статусы, таймер, кнопки копирования.

---

### `miniapp/react-app/src/App.css`
**Что делает:**
- Стили для модалки оплаты, кнопок выбора, QR и адреса.

---

## Примечания

- Снаружи (через Caddy) все API эндпоинты вызываются как `/api/...`, например IPN: `/api/payments/ipn`.
- QR строится по deep-link (например `tron:<address>?amount=<...>`), чтобы кошельки могли открыть оплату на телефоне.

