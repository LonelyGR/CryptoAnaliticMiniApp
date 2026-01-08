#!/bin/bash
echo "========================================"
echo "Создание .env файла для React приложения"
echo "========================================"
echo ""

read -p "Введите URL вашего backend сервера (например: https://abc123.ngrok.io): " API_URL

if [ -z "$API_URL" ]; then
    echo "[ОШИБКА] URL не введен!"
    exit 1
fi

echo ""
echo "Создание файла .env..."
echo "REACT_APP_API_URL=$API_URL" > .env

echo ""
echo "[OK] Файл .env создан!"
echo ""
echo "Содержимое:"
cat .env
echo ""
echo "========================================"
echo "ВАЖНО: Перезапустите React приложение!"
echo "========================================"
echo ""
echo "1. Остановите приложение (Ctrl+C)"
echo "2. Запустите снова: npm start"
echo ""

