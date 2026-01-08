#!/bin/bash

echo "========================================"
echo "Настройка виртуального окружения Backend"
echo "========================================"
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "[ОШИБКА] Python3 не найден! Установите Python 3.8 или выше."
    exit 1
fi

echo "[1/4] Создание виртуального окружения..."
if [ -d "venv" ]; then
    echo "Виртуальное окружение уже существует. Пропускаем создание."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ОШИБКА] Не удалось создать виртуальное окружение!"
        exit 1
    fi
    echo "[OK] Виртуальное окружение создано."
fi

echo ""
echo "[2/4] Активация виртуального окружения..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось активировать виртуальное окружение!"
    exit 1
fi
echo "[OK] Виртуальное окружение активировано."

echo ""
echo "[3/4] Обновление pip..."
python -m pip install --upgrade pip

echo ""
echo "[4/4] Установка зависимостей..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось установить зависимости!"
    exit 1
fi
echo "[OK] Зависимости установлены."

echo ""
echo "========================================"
echo "Настройка завершена успешно!"
echo "========================================"
echo ""
echo "Для запуска сервера выполните:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""

