@echo off
echo ============================================================
echo ПЕРЕЗАПУСК REACT ПРИЛОЖЕНИЯ С ОЧИСТКОЙ КЭША
echo ============================================================
echo.

echo [1/3] Остановка текущего процесса...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] Очистка кэша...
if exist node_modules\.cache (
    rmdir /s /q node_modules\.cache
    echo Кэш очищен
) else (
    echo Кэш не найден (это нормально)
)

echo [3/3] Проверка .env файла...
if exist .env (
    echo .env файл найден:
    type .env
    echo.
) else (
    echo ВНИМАНИЕ: .env файл не найден!
    echo Создайте файл .env с содержимым:
    echo REACT_APP_API_URL=https://ваш-url.com
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ЗАПУСК REACT ПРИЛОЖЕНИЯ
echo ============================================================
echo.
echo Откройте консоль браузера (F12) и проверьте:
echo - API Base URL configured: должен быть ваш URL
echo - REACT_APP_API_URL env: должен быть ваш URL
echo.
echo Нажмите Ctrl+C чтобы остановить
echo.

npm start

