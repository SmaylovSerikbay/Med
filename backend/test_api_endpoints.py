#!/usr/bin/env python
"""
Проверка API endpoints - реальные запросы к серверу
Проверяет что все endpoints доступны и возвращают данные
"""
import requests
import json

API_URL = 'http://localhost:8000/api'

print("="*70)
print("ПРОВЕРКА API ENDPOINTS")
print("="*70)

# Сначала нужно авторизоваться, но для проверки структуры можно проверить без токена
# (большинство endpoints требуют авторизации)

endpoints_to_check = [
    # Авторизация (публичные)
    ('POST', '/auth/send-otp/', {'phone_number': '77085446945'}),
    # Организации (требуют авторизации)
    ('GET', '/organizations/organizations/', None),
    ('GET', '/organizations/partnerships/', None),
    ('GET', '/organizations/employees/', None),
    # Документы
    ('GET', '/documents/documents/', None),
    # Осмотры
    ('GET', '/examinations/examinations/', None),
]

print("\nПроверка endpoints (без токена, только структура):")
print("-" * 70)

for method, endpoint, data in endpoints_to_check:
    url = f"{API_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        status = response.status_code
        if status == 401:
            print(f"  ✅ {method} {endpoint} - требует авторизации (401)")
        elif status == 200 or status == 201:
            print(f"  ✅ {method} {endpoint} - OK ({status})")
        elif status == 400:
            print(f"  ⚠️  {method} {endpoint} - Bad Request ({status})")
        else:
            print(f"  ❓ {method} {endpoint} - {status}")
    except requests.exceptions.ConnectionError:
        print(f"  ❌ {method} {endpoint} - Сервер не доступен")
    except Exception as e:
        print(f"  ❌ {method} {endpoint} - Ошибка: {e}")

print("\n" + "="*70)
print("Для полного тестирования нужно:")
print("1. Авторизоваться через UI")
print("2. Использовать полученный токен в заголовках Authorization: Bearer <token>")
print("="*70)

