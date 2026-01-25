# API Requests (GET/POST/PUT/DELETE)

Ниже перечислены **все текущие HTTP endpoints**, которые реально объявлены в `backend/app/routers/` и подключены в `backend/app/main.py`.

## Base URL

- **Local**: `http://localhost:8000`
- **ngrok (пример)**: `https://backend-username.eu.ngrok.io`

Во всех примерах ниже используйте переменную:

```bash
BASE_URL="https://backend-username.eu.ngrok.io"
```

PowerShell:

```powershell
$BASE_URL = "https://backend-username.eu.ngrok.io"
```

---

## Общие

### GET `/`

PowerShell:

```powershell
Invoke-RestMethod -Method Get -Uri "$BASE_URL/"
```

---

## NOWPayments (backend-only)

### POST `/create-payment`

Тело запроса (строго по NOWPayments `/v1/payment`):

```json
{
  "price_amount": 5,
  "price_currency": "usd",
  "pay_currency": "usdttrc20",
  "order_id": "test_001",
  "order_description": "Telegram Mini App test",
  "ipn_callback_url": "https://backend-username.eu.ngrok.io/payments/ipn"
}
```

PowerShell:

```powershell
$body = @{
  price_amount = 5
  price_currency = "usd"
  pay_currency = "usdttrc20"
  order_id = "test_001"
  order_description = "Telegram Mini App test"
  ipn_callback_url = "$BASE_URL/payments/ipn"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/create-payment" -ContentType "application/json" -Body $body
```

### GET `/currencies`

PowerShell:

```powershell
Invoke-RestMethod -Method Get -Uri "$BASE_URL/currencies"
```

### GET `/payment/{payment_id}`

PowerShell:

```powershell
$paymentId = 123456
Invoke-RestMethod -Method Get -Uri "$BASE_URL/payment/$paymentId"
```

### POST `/payments/ipn`

Webhook от NOWPayments. Заголовок подписи: `X-NOWPayments-Sig`.

---

## Users

### GET `/users/`

```powershell
Invoke-RestMethod -Method Get -Uri "$BASE_URL/users/"
```

### GET `/users/telegram/{telegram_id}`

```powershell
$tg = 123
Invoke-RestMethod -Method Get -Uri "$BASE_URL/users/telegram/$tg"
```

### GET `/users/{user_id}`

```powershell
$id = 1
Invoke-RestMethod -Method Get -Uri "$BASE_URL/users/$id"
```

### POST `/users/`

```powershell
$body = @{
  telegram_id = 123
  username = "test"
  first_name = "Test"
  last_name = "User"
  photo_url = $null
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/users/" -ContentType "application/json" -Body $body
```

### POST `/users/telegram/{telegram_id}`

Body опционален (можно отправить `{}` или не отправлять body).

```powershell
$tg = 123
$body = @{
  username = "newname"
  first_name = "Name"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/users/telegram/$tg" -ContentType "application/json" -Body $body
```

### PUT `/users/{user_id}/block?admin_telegram_id=...`

Body (embed=True): `{"is_blocked": true}`

```powershell
$userId = 1
$adminTg = 999
$body = @{ is_blocked = $true } | ConvertTo-Json

Invoke-RestMethod -Method Put -Uri "$BASE_URL/users/$userId/block?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

---

## Admins

### GET `/admins/`

```powershell
Invoke-RestMethod -Method Get -Uri "$BASE_URL/admins/"
```

### GET `/admins/telegram/{telegram_id}`

```powershell
$tg = 999
Invoke-RestMethod -Method Get -Uri "$BASE_URL/admins/telegram/$tg"
```

### GET `/admins/check/{telegram_id}`

```powershell
$tg = 999
Invoke-RestMethod -Method Get -Uri "$BASE_URL/admins/check/$tg"
```

### POST `/admins/`

```powershell
$body = @{ telegram_id = 999; role = "developer" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$BASE_URL/admins/" -ContentType "application/json" -Body $body
```

### PUT `/admins/{admin_id}`

```powershell
$adminId = 1
$body = @{ role = "admin" } | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "$BASE_URL/admins/$adminId" -ContentType "application/json" -Body $body
```

### DELETE `/admins/{admin_id}`

```powershell
$adminId = 1
Invoke-RestMethod -Method Delete -Uri "$BASE_URL/admins/$adminId"
```

### POST `/admins/clear-db?admin_telegram_id=...`

```powershell
$adminTg = 999
Invoke-RestMethod -Method Post -Uri "$BASE_URL/admins/clear-db?admin_telegram_id=$adminTg"
```

### POST `/admins/clear-data?admin_telegram_id=...&targets=...`

```powershell
$adminTg = 999
Invoke-RestMethod -Method Post -Uri "$BASE_URL/admins/clear-data?admin_telegram_id=$adminTg&targets=users&targets=bookings"
```

---

## Webinars

### GET `/webinars/`

```powershell
Invoke-RestMethod -Method Get -Uri "$BASE_URL/webinars/"
```

### GET `/webinars/{webinar_id}`

```powershell
$id = 1
Invoke-RestMethod -Method Get -Uri "$BASE_URL/webinars/$id"
```

### POST `/webinars/?admin_telegram_id=...`

```powershell
$adminTg = 999
$body = @{
  title = "Test webinar"
  date = "2026-01-31"
  time = "19:00"
  duration = "60m"
  speaker = "Speaker"
  status = "upcoming"
  description = "Desc"
  price_usd = 10.0
  price_eur = 0.0
  meeting_link = $null
  meeting_platform = $null
  recording_link = $null
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/webinars/?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

### PUT `/webinars/{webinar_id}?admin_telegram_id=...`

```powershell
$adminTg = 999
$id = 1
$body = @{
  title = "Updated"
  date = "2026-01-31"
  time = "19:30"
  status = "upcoming"
} | ConvertTo-Json

Invoke-RestMethod -Method Put -Uri "$BASE_URL/webinars/$id?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

### DELETE `/webinars/{webinar_id}?admin_telegram_id=...`

```powershell
$adminTg = 999
$id = 1
Invoke-RestMethod -Method Delete -Uri "$BASE_URL/webinars/$id?admin_telegram_id=$adminTg"
```

---

## Bookings

### GET `/bookings/`

```powershell
Invoke-RestMethod -Method Get -Uri "$BASE_URL/bookings/"
```

### GET `/bookings/consultations?admin_telegram_id=...`

```powershell
$adminTg = 999
Invoke-RestMethod -Method Get -Uri "$BASE_URL/bookings/consultations?admin_telegram_id=$adminTg"
```

### GET `/bookings/support-tickets?admin_telegram_id=...`

```powershell
$adminTg = 999
Invoke-RestMethod -Method Get -Uri "$BASE_URL/bookings/support-tickets?admin_telegram_id=$adminTg"
```

### GET `/bookings/user/{user_id}`

```powershell
$id = 1
Invoke-RestMethod -Method Get -Uri "$BASE_URL/bookings/user/$id"
```

### GET `/bookings/telegram/{telegram_id}`

```powershell
$tg = 123
Invoke-RestMethod -Method Get -Uri "$BASE_URL/bookings/telegram/$tg"
```

### POST `/bookings/`

```powershell
$body = @{
  user_id = 1
  webinar_id = 1
  type = "webinar"
  date = "2026-01-31"
  status = "pending"
  time = $null
  topic = $null
  message = $null
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/bookings/" -ContentType "application/json" -Body $body
```

### GET `/bookings/{booking_id}`

```powershell
$id = 1
Invoke-RestMethod -Method Get -Uri "$BASE_URL/bookings/$id"
```

### DELETE `/bookings/{booking_id}?admin_telegram_id=...`

```powershell
$adminTg = 999
$id = 1
Invoke-RestMethod -Method Delete -Uri "$BASE_URL/bookings/$id?admin_telegram_id=$adminTg"
```

### PUT `/bookings/{booking_id}/respond?admin_telegram_id=...`

```powershell
$adminTg = 999
$id = 1
$body = @{ admin_response = "Ответ" } | ConvertTo-Json

Invoke-RestMethod -Method Put -Uri "$BASE_URL/bookings/$id/respond?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

---

## Payments (DB payments table)

### POST `/payments/`

```powershell
$body = @{
  booking_id = 1
  amount = 10
  currency = "USD"
  payment_method = "crypto"
  payment_provider = "nowpayments"
  transaction_id = $null
  payment_metadata = $null
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/payments/" -ContentType "application/json" -Body $body
```

### GET `/payments/booking/{booking_id}`

```powershell
$bookingId = 1
Invoke-RestMethod -Method Get -Uri "$BASE_URL/payments/booking/$bookingId"
```

### GET `/payments/user/{user_id}`

```powershell
$userId = 1
Invoke-RestMethod -Method Get -Uri "$BASE_URL/payments/user/$userId"
```

### PUT `/payments/{payment_id}?admin_telegram_id=...`

```powershell
$adminTg = 999
$paymentId = 1
$body = @{ status = "completed" } | ConvertTo-Json

Invoke-RestMethod -Method Put -Uri "$BASE_URL/payments/$paymentId?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

### GET `/payments/?admin_telegram_id=...`

```powershell
$adminTg = 999
Invoke-RestMethod -Method Get -Uri "$BASE_URL/payments/?admin_telegram_id=$adminTg"
```

---

## Webinar materials

### GET `/webinar-materials/webinar/{webinar_id}`

```powershell
$webinarId = 1
Invoke-RestMethod -Method Get -Uri "$BASE_URL/webinar-materials/webinar/$webinarId"
```

### POST `/webinar-materials/?admin_telegram_id=...`

```powershell
$adminTg = 999
$body = @{
  webinar_id = 1
  title = "Slides"
  description = "PDF"
  file_url = "https://example.com/file.pdf"
  file_type = "pdf"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/webinar-materials/?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

### PUT `/webinar-materials/{material_id}?admin_telegram_id=...`

```powershell
$adminTg = 999
$materialId = 1
$body = @{
  webinar_id = 1
  title = "Updated title"
  description = "Updated"
  file_url = "https://example.com/file.pdf"
  file_type = "pdf"
} | ConvertTo-Json

Invoke-RestMethod -Method Put -Uri "$BASE_URL/webinar-materials/$materialId?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

### DELETE `/webinar-materials/{material_id}?admin_telegram_id=...`

```powershell
$adminTg = 999
$materialId = 1
Invoke-RestMethod -Method Delete -Uri "$BASE_URL/webinar-materials/$materialId?admin_telegram_id=$adminTg"
```

---

## Posts

### GET `/posts/`

```powershell
Invoke-RestMethod -Method Get -Uri "$BASE_URL/posts/"
```

### GET `/posts/{post_id}`

```powershell
$id = 1
Invoke-RestMethod -Method Get -Uri "$BASE_URL/posts/$id"
```

### POST `/posts/?admin_telegram_id=...`

```powershell
$adminTg = 999
$body = @{ title = "Post"; content = "Text" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$BASE_URL/posts/?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

### PUT `/posts/{post_id}?admin_telegram_id=...`

```powershell
$adminTg = 999
$id = 1
$body = @{ title = "Updated"; content = "Updated text" } | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "$BASE_URL/posts/$id?admin_telegram_id=$adminTg" -ContentType "application/json" -Body $body
```

### DELETE `/posts/{post_id}?admin_telegram_id=...`

```powershell
$adminTg = 999
$id = 1
Invoke-RestMethod -Method Delete -Uri "$BASE_URL/posts/$id?admin_telegram_id=$adminTg"
```

---

## Referrals

### GET `/referrals/{telegram_id}`

```powershell
$tg = 123
Invoke-RestMethod -Method Get -Uri "$BASE_URL/referrals/$tg"
```

### POST `/referrals/track`

```powershell
$body = @{
  referral_code = "abc123"
  referred_telegram_id = 555
  referred_username = "user"
  referred_first_name = "First"
  referred_last_name = "Last"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$BASE_URL/referrals/track" -ContentType "application/json" -Body $body
```

---

## Reminders

### POST `/reminders/check-and-send?admin_telegram_id=...`

```powershell
$adminTg = 999
Invoke-RestMethod -Method Post -Uri "$BASE_URL/reminders/check-and-send?admin_telegram_id=$adminTg"
```

### GET `/reminders/upcoming?admin_telegram_id=...`

```powershell
$adminTg = 999
Invoke-RestMethod -Method Get -Uri "$BASE_URL/reminders/upcoming?admin_telegram_id=$adminTg"
```

