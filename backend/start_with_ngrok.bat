@echo off
echo ========================================
echo Запуск Backend + ngrok для Telegram WebApp
echo ========================================
echo.

REM Проверка виртуального окружения
if not exist venv (
    echo [ОШИБКА] Виртуальное окружение не найдено!
    echo Запустите setup.bat для настройки окружения.
    pause
    exit /b 1
)

REM Активация виртуального окружения
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать виртуальное окружение!
    pause
    exit /b 1
)

echo [1/2] Запуск backend сервера...
start "Backend Server" cmd /k "python run.py"

echo.
echo [2/2] Ожидание запуска сервера...
timeout /t 3 /nobreak >nul

echo.
echo Запуск ngrok туннеля...
echo.
echo ВАЖНО: Скопируйте HTTPS URL из ngrok и обновите файл:
echo   miniapp/react-app/.env
echo.
echo Добавьте строку:
echo   REACT_APP_API_URL=https://ваш-ngrok-url.ngrok.io
echo.

start "ngrok Tunnel" cmd /k "ngrok http 8000"

echo.
echo ========================================
echo Backend и ngrok запущены!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Скопируйте HTTPS URL из окна ngrok
echo 2. Обновите miniapp/react-app/.env с этим URL
echo 3. Перезапустите React приложение
echo.
pause

