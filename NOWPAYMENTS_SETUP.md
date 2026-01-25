# NOWPayments интеграция — карта файлов

Этот документ описывает, какие файлы отвечают за приём крипто‑платежей через NOWPayments, как устроен поток и где править поведение.

## Основной поток оплаты

1. Пользователь нажимает «Оплатить» в вебинарах.
2. Фронт вызывает бэкенд `POST /create-payment`.
3. Бэкенд создаёт invoice, затем payment по invoice.
4. Фронт получает `payment_link`/`invoice_url` + `pay_address` и показывает выбор:
   - «Оплата через кошелёк» (ссылка)
   - «Оплата через QR» (QR по ссылке)
5. Фронт каждые 10 секунд опрашивает `/payment/{payment_id}`.
6. Вебхук NOWPayments подтверждает оплату и обновляет Booking/Payment в БД.

---

## Backend

### `backend/app/routers/nowpayments.py`
**Что делает:**
- Эндпоинты:
  - `GET /currencies`
  - `POST /create-payment`
  - `GET /payment/{payment_id}`
  - `POST /webhook/nowpayments`
- Создаёт **invoice** (`/invoice`) и **payment по invoice** (`/invoice-payment`).
- Формирует `payment_link` и возвращает его на фронт.
- Обновляет платежи/бронь в БД.
- Проверяет подписи webhook и идемпотентность.

**Ключевые места:**
- Формирование invoice и payment.
- Присвоение `invoice_url` и `payment_link`.
- Сохранение `payment_metadata` в БД.
- Маппинг статусов NOWPayments → `payments.status` и `bookings.payment_status`.

---

### `backend/app/services/nowpayments.py`
**Что делает:**
- Работа с NOWPayments API через `httpx`.
- Методы:
  - `get_currencies()`
  - `create_invoice()`
  - `create_invoice_payment()`
  - `create_payment()` (прямой платеж, сейчас не используется)
  - `get_payment()`
  - `get_min_amount()`

---

### `backend/app/schemas/nowpayments.py`
**Что делает:**
- Pydantic‑модели для всех запросов и ответов NOWPayments.
- Нормализация `purchase_id` (иногда приходит числом).
- Поля `invoice_url`, `payment_url`, `payment_link` доступны на фронте.

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

### `.env (backend)`
**Что нужно:**
- `NOWPAYMENTS_API_KEY=...`
- `NOWPAYMENTS_IPN_SECRET=...`
- `NOWPAYMENTS_IPN_CALLBACK_URL=https://<домен>/webhook/nowpayments` (желательно)

---

## Frontend

### `miniapp/react-app/src/screens/Bookings.js`
**Что делает:**
- Кнопка «Оплатить» открывает модалку с `PaymentFlow`.
- Передаёт:
  - `orderId` (booking)
  - `amount` (цена в USDT)
  - `priceCurrency` = `usdttrc20`
  - `fixedPayCurrency` = `usdttrc20`

---

### `miniapp/react-app/src/components/PaymentFlow.js`
**Что делает:**
- Загружает `payment_link` и `pay_address`.
- Показывает выбор:
  - «Оплата через кошелёк» (ссылка)
  - «Оплата через QR» (QR по ссылке)
- Поллит `/payment/{payment_id}`.
- Показывает статусы, таймер, кнопки копирования.

---

### `miniapp/react-app/src/App.css`
**Что делает:**
- Стили для модалки оплаты, кнопок выбора, QR и адреса.

---

## Примечания

- NOWPayments может не отдавать `payment_url`, поэтому используется `invoice_url`.
- QR строится **по ссылке**, чтобы открывать оплату на телефоне.
- Если нужно вернуть «прямую оплату» без invoice — можно вернуть `POST /payment`,
  но тогда не будет кликабельной ссылки для телефона.

