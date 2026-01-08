@echo off
echo ========================================
echo Запуск Backend + Cloudflare Tunnel для Telegram WebApp
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
echo Запуск Cloudflare Tunnel...
echo.
echo ВАЖНО: Скопируйте HTTPS URL из Cloudflare Tunnel и обновите файл:
echo   miniapp/react-app/.env
echo.
echo Добавьте строку:
echo   REACT_APP_API_URL=https://ваш-cloudflare-url.trycloudflare.com
echo.

REM Проверка установки cloudflared
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] cloudflared не установлен!
    echo.
    echo Установите cloudflared:
    echo   winget install --id Cloudflare.cloudflared
    echo   Или скачайте с: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
    echo.
    pause
    exit /b 1
)

start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000"

echo.
echo ========================================
echo Backend и Cloudflare Tunnel запущены!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Скопируйте HTTPS URL из окна Cloudflare Tunnel
echo 2. Обновите miniapp/react-app/.env с этим URL
echo 3. Перезапустите React приложение
echo.
pause

