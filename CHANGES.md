# Изменения в проекте CryptoAnaliticMiniApp (Актуально на момент 06.01.2026)

## Резюме
Проект полностью переработан для работы с базой данных. Все данные пользователей, вебинары и записи теперь хранятся в базе данных SQLite и загружаются через REST API.

## Backend (FastAPI)

### Новые модели базы данных

1. **Webinar** (`backend/app/models/webinar.py`)
   - Модель для хранения информации о вебинарах
   - Поля: id, title, date, time, duration, speaker, status, description

2. **Обновленная модель User** (`backend/app/models/user.py`)
   - Добавлены поля: last_name, photo_url
   - Все поля теперь nullable для гибкости

3. **Обновленная модель Booking** (`backend/app/models/booking.py`)
   - Добавлены поля: webinar_id, time, topic, message
   - Поддержка записей на вебинары и консультации

### Новые схемы Pydantic

Созданы схемы для валидации данных:
- `backend/app/schemas/user.py` - UserCreate, UserResponse
- `backend/app/schemas/booking.py` - BookingCreate, BookingResponse
- `backend/app/schemas/webinar.py` - WebinarCreate, WebinarResponse

### Новые API эндпоинты

#### Пользователи (`/users`)
- `GET /users/` - список всех пользователей
- `GET /users/{user_id}` - пользователь по ID
- `GET /users/telegram/{telegram_id}` - пользователь по Telegram ID
- `POST /users/` - создать пользователя
- `POST /users/telegram/{telegram_id}` - создать/обновить пользователя по Telegram ID

#### Вебинары (`/webinars`)
- `GET /webinars/` - список всех вебинаров
- `GET /webinars/{webinar_id}` - вебинар по ID
- `POST /webinars/` - создать вебинар

#### Записи (`/bookings`)
- `GET /bookings/` - список всех записей
- `GET /bookings/user/{user_id}` - записи пользователя по user_id
- `GET /bookings/telegram/{telegram_id}` - записи пользователя по telegram_id
- `GET /bookings/{booking_id}` - запись по ID
- `POST /bookings/` - создать запись

### Файлы для запуска

- `backend/run.py` - скрипт для запуска сервера
- `backend/start.bat` - батник для Windows
- `backend/start.sh` - скрипт для Linux/Mac
- `backend/README.md` - документация по запуску

## Miniapp (React)

### Новый API сервис

Создан `miniapp/react-app/src/services/api.js` с функциями:
- `getUserByTelegramId()` - получить пользователя из БД
- `createOrUpdateUser()` - создать/обновить пользователя
- `getWebinars()` - получить список вебинаров
- `getUserBookings()` - получить записи пользователя
- `createBooking()` - создать запись
- `checkApiHealth()` - проверить доступность API

### Обновленные компоненты

1. **App.js**
   - Автоматическая загрузка пользователя из БД при запуске
   - Создание/обновление пользователя в БД при первом входе
   - Отслеживание состояния подключения к API
   - Предупреждение при недоступности сервера

2. **Bookings.js** (было Bookings.js)
   - Загрузка вебинаров из БД вместо моков
   - Функционал записи на вебинар с сохранением в БД
   - Обработка ошибок подключения к серверу
   - Отображение состояния загрузки

3. **Profile.js**
   - Загрузка записей пользователя из БД
   - Отображение данных пользователя из БД
   - Связывание записей с вебинарами через webinar_id
   - Обработка ошибок подключения

4. **Support.js**
   - Функционал записи на консультацию с сохранением в БД
   - Валидация формы
   - Обработка ошибок подключения

5. **Home.js**
   - Передача параметра apiConnected для будущего использования

### Обработка ошибок

Все компоненты теперь:
- Проверяют доступность API перед загрузкой данных
- Показывают предупреждения при недоступности сервера
- Продолжают работать даже при недоступности сервера (без данных)
- Отображают состояния загрузки

## Как запустить

### Backend

1. Перейдите в папку `backend`
2. Создайте виртуальное окружение (если еще не создано):
   ```bash
   python -m venv venv
   ```
3. Активируйте виртуальное окружение:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Запустите сервер:
   ```bash
   python run.py
   ```
   Или используйте `start.bat` (Windows) или `start.sh` (Linux/Mac)

Сервер будет доступен по адресу: http://localhost:8000
Документация API: http://localhost:8000/docs

### Miniapp

1. Перейдите в папку `miniapp/react-app`
2. Установите зависимости (если еще не установлены):
   ```bash
   npm install
   ```
3. Создайте файл `.env` (если нужно изменить URL API):
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```
4. Запустите приложение:
   ```bash
   npm start
   ```

## Важные замечания

1. **База данных**: SQLite база данных `db.sqlite3` создается автоматически в папке `backend` при первом запуске сервера.

2. **CORS**: Backend настроен на разрешение запросов с любых источников (`allow_origins=["*"]`). Для production рекомендуется ограничить это.

3. **Telegram WebApp**: Miniapp получает данные пользователя из `window.Telegram.WebApp.initDataUnsafe.user` и синхронизирует их с базой данных.

4. **Обработка ошибок**: При недоступности сервера приложение продолжает работать, но данные не отображаются. Пользователь видит предупреждение.

5. **Вебинары**: Все фальшивые/моковые данные вебинаров удалены. Теперь вебинары загружаются только из базы данных.

## Следующие шаги

1. Добавить вебинары в базу данных через API или админ-панель
2. Реализовать отправку обращений в поддержку (если требуется)
3. Добавить аутентификацию и авторизацию (если требуется)
4. Настроить production окружение

