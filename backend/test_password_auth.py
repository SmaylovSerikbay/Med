"""
Тестовый скрипт для проверки авторизации по паролю
Запуск: python test_password_auth.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_password_authentication():
    """Тестирование полного цикла авторизации по паролю"""
    
    print("=" * 60)
    print("ТЕСТ АВТОРИЗАЦИИ ПО ПАРОЛЮ")
    print("=" * 60)
    
    # Тестовый номер телефона
    phone = "77001234567"
    password = "testpass123"
    
    # Шаг 1: Отправка OTP для первичной регистрации
    print("\n1. Отправка OTP кода...")
    response = requests.post(f"{BASE_URL}/auth/send-otp/", json={
        "phone_number": phone
    })
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Ошибка отправки OTP")
        return
    
    # Шаг 2: Ввод OTP кода (в реальности нужно получить из WhatsApp)
    otp_code = input("\nВведите OTP код из WhatsApp: ")
    
    print("\n2. Проверка OTP кода...")
    response = requests.post(f"{BASE_URL}/auth/verify-otp/", json={
        "phone_number": phone,
        "code": otp_code
    })
    print(f"Статус: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Ошибка проверки OTP")
        print(f"Ответ: {response.json()}")
        return
    
    data = response.json()
    access_token = data['tokens']['access']
    print(f"✅ Успешный вход через OTP")
    print(f"Access Token: {access_token[:50]}...")
    
    # Шаг 3: Установка пароля
    print("\n3. Установка пароля...")
    response = requests.post(f"{BASE_URL}/auth/set-password/", 
        headers={"Authorization": f"Bearer {access_token}"},
        json={"new_password": password}
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Ошибка установки пароля")
        return
    
    print("✅ Пароль успешно установлен")
    
    # Шаг 4: Проверка профиля
    print("\n4. Проверка профиля...")
    response = requests.get(f"{BASE_URL}/auth/profile/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Статус: {response.status_code}")
    profile = response.json()
    print(f"Has password: {profile['user'].get('has_password', False)}")
    
    # Шаг 5: Вход по паролю
    print("\n5. Вход по паролю...")
    response = requests.post(f"{BASE_URL}/auth/login-password/", json={
        "phone_number": phone,
        "password": password
    })
    print(f"Статус: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Ошибка входа по паролю")
        print(f"Ответ: {response.json()}")
        return
    
    data = response.json()
    new_access_token = data['tokens']['access']
    print(f"✅ Успешный вход по паролю")
    print(f"Access Token: {new_access_token[:50]}...")
    
    # Шаг 6: Изменение пароля
    new_password = "newpass456"
    print("\n6. Изменение пароля...")
    response = requests.post(f"{BASE_URL}/auth/set-password/",
        headers={"Authorization": f"Bearer {new_access_token}"},
        json={
            "current_password": password,
            "new_password": new_password
        }
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Ошибка изменения пароля")
        return
    
    print("✅ Пароль успешно изменен")
    
    # Шаг 7: Вход с новым паролем
    print("\n7. Вход с новым паролем...")
    response = requests.post(f"{BASE_URL}/auth/login-password/", json={
        "phone_number": phone,
        "password": new_password
    })
    print(f"Статус: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Ошибка входа с новым паролем")
        print(f"Ответ: {response.json()}")
        return
    
    print("✅ Успешный вход с новым паролем")
    
    # Шаг 8: Сброс пароля
    print("\n8. Запрос на сброс пароля...")
    response = requests.post(f"{BASE_URL}/auth/reset-password/request/", json={
        "phone_number": phone
    })
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Ошибка запроса сброса пароля")
        return
    
    reset_code = input("\nВведите код для сброса пароля из WhatsApp: ")
    reset_password = "resetpass789"
    
    print("\n9. Подтверждение сброса пароля...")
    response = requests.post(f"{BASE_URL}/auth/reset-password/confirm/", json={
        "phone_number": phone,
        "code": reset_code,
        "new_password": reset_password
    })
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Ошибка подтверждения сброса пароля")
        return
    
    print("✅ Пароль успешно сброшен")
    
    # Шаг 10: Вход с новым паролем после сброса
    print("\n10. Вход с паролем после сброса...")
    response = requests.post(f"{BASE_URL}/auth/login-password/", json={
        "phone_number": phone,
        "password": reset_password
    })
    print(f"Статус: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Ошибка входа после сброса")
        print(f"Ответ: {response.json()}")
        return
    
    print("✅ Успешный вход после сброса пароля")
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)


def test_wrong_password():
    """Тест неверного пароля"""
    print("\n" + "=" * 60)
    print("ТЕСТ НЕВЕРНОГО ПАРОЛЯ")
    print("=" * 60)
    
    phone = "77001234567"
    wrong_password = "wrongpassword"
    
    print("\nПопытка входа с неверным паролем...")
    response = requests.post(f"{BASE_URL}/auth/login-password/", json={
        "phone_number": phone,
        "password": wrong_password
    })
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 401:
        print("✅ Неверный пароль корректно отклонен")
    else:
        print("❌ Ожидался статус 401")


if __name__ == "__main__":
    print("\n🚀 Запуск тестов авторизации по паролю\n")
    print("Убедитесь, что:")
    print("1. Backend запущен на http://localhost:8000")
    print("2. Green-API настроен для отправки WhatsApp сообщений")
    print("3. У вас есть доступ к WhatsApp для получения кодов\n")
    
    choice = input("Выберите тест:\n1. Полный тест\n2. Тест неверного пароля\n3. Оба теста\n\nВыбор: ")
    
    if choice == "1":
        test_password_authentication()
    elif choice == "2":
        test_wrong_password()
    elif choice == "3":
        test_password_authentication()
        test_wrong_password()
    else:
        print("Неверный выбор")
