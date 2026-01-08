"""
Скрипт для автоматической настройки ngrok туннеля
Использование: python setup_ngrok.py
"""
import subprocess
import sys
import time
import requests
import json

def check_ngrok_installed():
    """Проверка установки ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_ngrok_url():
    """Получение URL ngrok туннеля"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    return tunnel.get('public_url')
    except:
        pass
    return None

def start_ngrok(port=8000):
    """Запуск ngrok туннеля"""
    print("="*60)
    print("НАСТРОЙКА NGROK ДЛЯ TELEGRAM WEBAPP")
    print("="*60)
    print()
    
    if not check_ngrok_installed():
        print("✗ ОШИБКА: ngrok не установлен!")
        print()
        print("Установите ngrok:")
        print("1. Скачайте с https://ngrok.com/download")
        print("2. Распакуйте и добавьте в PATH")
        print("3. Или используйте: pip install pyngrok")
        print()
        print("Альтернатива: используйте другой туннель (localtunnel, serveo и т.д.)")
        return None
    
    print("✓ ngrok установлен")
    print()
    print(f"Запуск ngrok туннеля на порт {port}...")
    print("⚠ ВАЖНО: ngrok должен быть запущен в отдельном терминале!")
    print()
    print("Выполните в НОВОМ терминале:")
    print(f"  ngrok http {port}")
    print()
    print("Или используйте команду:")
    print(f"  start ngrok http {port}")
    print()
    
    input("Нажмите Enter после запуска ngrok...")
    
    print()
    print("Проверка ngrok туннеля...")
    time.sleep(2)
    
    url = get_ngrok_url()
    if url:
        print(f"✓ Туннель активен: {url}")
        print()
        print("="*60)
        print("НАСТРОЙКА REACT ПРИЛОЖЕНИЯ")
        print("="*60)
        print()
        print(f"Создайте или обновите файл: miniapp/react-app/.env")
        print()
        print("Содержимое:")
        print(f"REACT_APP_API_URL={url}")
        print()
        print("После этого перезапустите React приложение!")
        return url
    else:
        print("✗ Не удалось получить URL туннеля")
        print("Убедитесь, что ngrok запущен и доступен на http://localhost:4040")
        return None

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            pass
    
    url = start_ngrok(port)
    if url:
        print()
        print("="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"Backend доступен по адресу: {url}")
        print(f"Обновите .env файл и перезапустите React приложение")
    else:
        sys.exit(1)

