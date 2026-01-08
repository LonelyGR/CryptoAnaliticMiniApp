@echo off
echo ========================================
echo Настройка виртуального окружения Backend
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден! Установите Python 3.8 или выше.
    pause
    exit /b 1
)

echo [1/4] Создание виртуального окружения...
if exist venv (
    echo Виртуальное окружение уже существует. Пропускаем создание.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать виртуальное окружение!
        pause
        exit /b 1
    )
    echo [OK] Виртуальное окружение создано.
)

echo.
echo [2/4] Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать виртуальное окружение!
    pause
    exit /b 1
)
echo [OK] Виртуальное окружение активировано.

echo.
echo [3/4] Обновление pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Не удалось обновить pip, продолжаем...
)

echo.
echo [4/4] Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости!
    pause
    exit /b 1
)
echo [OK] Зависимости установлены.

echo.
echo ========================================
echo Настройка завершена успешно!
echo ========================================
echo.
echo Для запуска сервера выполните:
echo   venv\Scripts\activate
echo   python run.py
echo.
pause

