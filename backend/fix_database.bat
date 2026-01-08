@echo off
echo ========================================
echo Исправление структуры базы данных
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

echo Запуск миграции базы данных...
echo.

python migrate_db.py

echo.
pause

