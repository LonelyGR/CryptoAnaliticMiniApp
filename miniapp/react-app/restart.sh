#!/bin/bash

echo "============================================================"
echo "ПЕРЕЗАПУСК REACT ПРИЛОЖЕНИЯ С ОЧИСТКОЙ КЭША"
echo "============================================================"
echo ""

echo "[1/3] Остановка текущего процесса..."
pkill -f "react-scripts" 2>/dev/null || true
sleep 2

echo "[2/3] Очистка кэша..."
if [ -d "node_modules/.cache" ]; then
    rm -rf node_modules/.cache
    echo "Кэш очищен"
else
    echo "Кэш не найден (это нормально)"
fi

echo "[3/3] Проверка .env файла..."
if [ -f ".env" ]; then
    echo ".env файл найден:"
    cat .env
    echo ""
else
    echo "ВНИМАНИЕ: .env файл не найден!"
    echo "Создайте файл .env с содержимым:"
    echo "REACT_APP_API_URL=https://ваш-url.com"
    echo ""
    exit 1
fi

echo ""
echo "============================================================"
echo "ЗАПУСК REACT ПРИЛОЖЕНИЯ"
echo "============================================================"
echo ""
echo "Откройте консоль браузера (F12) и проверьте:"
echo "- API Base URL configured: должен быть ваш URL"
echo "- REACT_APP_API_URL env: должен быть ваш URL"
echo ""
echo "Нажмите Ctrl+C чтобы остановить"
echo ""

npm start

