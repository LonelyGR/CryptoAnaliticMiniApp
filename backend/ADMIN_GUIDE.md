# Руководство по админке

## Настройка

### 1. Добавление таблицы admins в базу данных

```bash
cd backend
python migrate_db_admins.py
```

### 2. Добавление первого администратора

```bash
python add_first_admin.py
```

Это создаст администратора:
- Telegram ID: `6989481318`
- Должность: `разработчик`

## API для администраторов

### Проверка статуса администратора

```bash
GET /admins/check/{telegram_id}
```

Ответ:
```json
{
  "is_admin": true,
  "admin_id": 1,
  "telegram_id": 6989481318,
  "role": "разработчик"
}
```

### Создание вебинара (только для админов)

```bash
POST /webinars/?admin_telegram_id=6989481318
Content-Type: application/json

{
  "title": "Название вебинара",
  "date": "2024-12-20",
  "time": "18:00",
  "duration": "2 часа",
  "speaker": "Имя спикера",
  "status": "upcoming",
  "description": "Описание вебинара"
}
```

### Обновление вебинара (только для админов)

```bash
PUT /webinars/{webinar_id}?admin_telegram_id=6989481318
Content-Type: application/json

{
  "title": "Обновленное название",
  ...
}
```

### Удаление вебинара (только для админов)

```bash
DELETE /webinars/{webinar_id}?admin_telegram_id=6989481318
```

## Информация о пользователе

При получении пользователя через API, теперь возвращается дополнительная информация:

```json
{
  "id": 1,
  "telegram_id": 6989481318,
  "username": "username",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "photo_url": "url",
  "is_admin": true,
  "role": "разработчик"
}
```

Поля:
- `is_admin` - является ли пользователь администратором
- `role` - должность администратора (если админ)

## Примеры использования

### Создание вебинара через curl

```bash
curl -X POST "http://localhost:8000/webinars/?admin_telegram_id=6989481318" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Основы криптотрейдинга",
    "date": "2024-12-20",
    "time": "18:00",
    "duration": "2 часа",
    "speaker": "Иван Петров",
    "status": "upcoming",
    "description": "Изучите базовые принципы торговли криптовалютами"
  }'
```

### Проверка статуса админа

```bash
curl http://localhost:8000/admins/check/6989481318
```

## Безопасность

- Только пользователи с записью в таблице `admins` могут создавать/обновлять/удалять вебинары
- При попытке доступа без прав администратора возвращается ошибка 403
- Telegram ID администратора передается как query параметр `admin_telegram_id`

