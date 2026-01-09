#!/usr/bin/env python3
"""
Скрипт для проверки CORS заголовков на сервере
"""
import sys
import urllib.request
import json

def test_cors(url):
    """Проверяет CORS заголовки на указанном URL"""
    print(f"Проверяю CORS на: {url}")
    print("=" * 60)
    
    try:
        # Делаем OPTIONS запрос (preflight)
        req = urllib.request.Request(url, method='OPTIONS')
        req.add_header('Origin', 'http://localhost:3000')
        req.add_header('Access-Control-Request-Method', 'GET')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"✅ OPTIONS запрос успешен: {response.status}")
            print("\nЗаголовки ответа:")
            for header, value in response.headers.items():
                if 'access-control' in header.lower():
                    print(f"  {header}: {value}")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                print("\n✅ CORS заголовки присутствуют!")
            else:
                print("\n❌ CORS заголовки отсутствуют!")
                
    except urllib.error.HTTPError as e:
        print(f"⚠️ HTTP ошибка: {e.code} {e.reason}")
        if e.code == 405:
            print("   (405 Method Not Allowed - это нормально, если OPTIONS не обрабатывается)")
        print("\nПроверяю GET запрос...")
        # Пробуем GET запрос
        try:
            req = urllib.request.Request(url)
            req.add_header('Origin', 'http://localhost:3000')
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"✅ GET запрос успешен: {response.status}")
                data = json.loads(response.read().decode())
                print(f"   Ответ: {data}")
        except Exception as e2:
            print(f"❌ GET запрос тоже не работает: {e2}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nВозможные причины:")
        print("1. Сервер не запущен")
        print("2. Неправильный URL")
        print("3. Проблемы с сетью")

if __name__ == "__main__":
    # Тестируем локальный сервер
    print("ТЕСТ 1: Локальный сервер")
    test_cors("http://localhost:8000/")
    
    print("\n" + "=" * 60 + "\n")
    
    # Если передан URL как аргумент, тестируем его тоже
    if len(sys.argv) > 1:
        print(f"ТЕСТ 2: Удаленный сервер ({sys.argv[1]})")
        test_cors(sys.argv[1])



