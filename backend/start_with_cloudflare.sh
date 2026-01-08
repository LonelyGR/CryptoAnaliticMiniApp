#!/bin/bash
echo "========================================"
echo "Запуск Backend + Cloudflare Tunnel для Telegram WebApp"
echo "========================================"
echo ""

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "[ОШИБКА] Виртуальное окружение не найдено!"
    echo "Запустите setup.sh для настройки окружения."
    exit 1
fi

# Активация виртуального окружения
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось активировать виртуальное окружение!"
    exit 1
fi

echo "[1/2] Запуск backend сервера..."
python run.py &
BACKEND_PID=$!

echo ""
echo "[2/2] Ожидание запуска сервера..."
sleep 3

echo ""
echo "Запуск Cloudflare Tunnel..."
echo ""
echo "ВАЖНО: Скопируйте HTTPS URL из Cloudflare Tunnel и обновите файл:"
echo "  miniapp/react-app/.env"
echo ""
echo "Добавьте строку:"
echo "  REACT_APP_API_URL=https://ваш-cloudflare-url.trycloudflare.com"
echo ""

# Проверка установки cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "[ОШИБКА] cloudflared не установлен!"
    echo ""
    echo "Установите cloudflared:"
    echo "  brew install cloudflared  # Mac"
    echo "  Или скачайте с: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
    echo ""
    exit 1
fi

cloudflared tunnel --url http://localhost:8000 &
CF_PID=$!

echo ""
echo "========================================"
echo "Backend и Cloudflare Tunnel запущены!"
echo "========================================"
echo ""
echo "Следующие шаги:"
echo "1. Скопируйте HTTPS URL из Cloudflare Tunnel"
echo "2. Обновите miniapp/react-app/.env с этим URL"
echo "3. Перезапустите React приложение"
echo ""
echo "Для остановки нажмите Ctrl+C"

# Ожидание
wait

