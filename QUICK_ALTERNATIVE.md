# 🚀 Быстрая альтернатива ngrok для Backend

## ⚡ localtunnel (Самый простой вариант)

### 1. Установите localtunnel:
```bash
npm install -g localtunnel
```

### 2. Запустите backend + localtunnel:

**Windows:**
```bash
cd backend
start_with_localtunnel.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x start_with_localtunnel.sh
./start_with_localtunnel.sh
```

Или вручную:
```bash
# Терминал 1: Backend
cd backend
python run.py

# Терминал 2: localtunnel
lt --port 8000
```

### 3. Скопируйте URL

Вы получите что-то вроде:
```
your url is: https://random-name.loca.lt
```

### 4. Обновите `.env`:

Создайте `miniapp/react-app/.env`:
```
REACT_APP_API_URL=https://random-name.loca.lt
```

### 5. Перезапустите React:
```bash
cd miniapp/react-app
npm start
```

## ✅ Готово!

---

## 🌐 Cloudflare Tunnel (Альтернатива)

### Установка:
- Windows: `winget install --id Cloudflare.cloudflared`
- Mac: `brew install cloudflared`
- Linux: скачайте с сайта Cloudflare

### Запуск:
```bash
cd backend
start_with_cloudflare.bat  # Windows
# или
./start_with_cloudflare.sh  # Linux/Mac
```

Или вручную:
```bash
cloudflared tunnel --url http://localhost:8000
```

---

## 📋 Сравнение альтернатив

| Инструмент | Установка | Стабильность | URL меняется |
|------------|-----------|--------------|--------------|
| **localtunnel** | ⭐⭐⭐ Очень просто | ⭐⭐⭐ Хорошая | Да |
| **Cloudflare Tunnel** | ⭐⭐ Средняя | ⭐⭐⭐⭐ Отличная | Да |
| **serveo** | ⭐⭐⭐ Есть SSH | ⭐⭐ Средняя | Да (можно зафиксировать) |

**Рекомендация:** Используйте **localtunnel** - самый простой вариант!

Подробнее: `backend/ALTERNATIVES_TO_NGROK.md`

