@echo off
echo ========================================
echo Создание .env файла для React приложения
echo ========================================
echo.

set /p API_URL="Введите URL вашего backend сервера (например: https://abc123.ngrok.io): "

if "%API_URL%"=="" (
    echo [ОШИБКА] URL не введен!
    pause
    exit /b 1
)

echo.
echo Создание файла .env...
echo REACT_APP_API_URL=%API_URL% > .env

echo.
echo [OK] Файл .env создан!
echo.
echo Содержимое:
type .env
echo.
echo ========================================
echo ВАЖНО: Перезапустите React приложение!
echo ========================================
echo.
echo 1. Остановите приложение (Ctrl+C)
echo 2. Запустите снова: npm start
echo.
pause

