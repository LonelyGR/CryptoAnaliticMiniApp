# Настройка Backend - Первый запуск

## Быстрая настройка

### Windows
```bash
cd backend
setup.bat
```

### Linux/Mac
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

Скрипт автоматически:
1. ✅ Создаст виртуальное окружение `venv`
2. ✅ Активирует его
3. ✅ Установит все зависимости из `requirements.txt`

## Что происходит при настройке

1. **Создание виртуального окружения**
   - Создается папка `venv/` с изолированным Python окружением
   - Это нужно, чтобы не смешивать зависимости проекта с системным Python

2. **Установка зависимостей**
   - `fastapi` - веб-фреймворк
   - `uvicorn` - ASGI сервер
   - `sqlalchemy` - ORM для работы с БД
   - `pydantic` - валидация данных
   - `requests` - для тестирования

## После настройки

### Запуск сервера

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

Или вручную:
```bash
# Активируйте виртуальное окружение
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Запустите сервер
python run.py
```

## Проверка установки

После настройки проверьте:

```bash
# Активируйте виртуальное окружение
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Проверьте установленные пакеты
pip list

# Должны быть видны: fastapi, uvicorn, sqlalchemy, pydantic, requests
```

## Решение проблем

### Ошибка: "python не найден"
- Установите Python 3.8 или выше
- Убедитесь, что Python добавлен в PATH

### Ошибка: "venv не найден"
- Обновите pip: `python -m pip install --upgrade pip`
- Установите venv: `python -m pip install virtualenv`

### Ошибка при установке зависимостей
- Проверьте интернет-соединение
- Попробуйте обновить pip: `python -m pip install --upgrade pip`
- Убедитесь, что используете правильную версию Python (3.8+)

## Важно

- Виртуальное окружение нужно активировать каждый раз перед работой с проектом
- Файл `venv/` добавлен в `.gitignore` - не коммитьте его в git
- После клонирования проекта всегда запускайте `setup.bat` или `setup.sh`

