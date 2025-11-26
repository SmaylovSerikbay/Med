# Руководство по авторизации ProfMed.kz

## Обзор

Система поддерживает два способа авторизации:
1. **WhatsApp OTP** - быстрый вход через код в WhatsApp (основной способ)
2. **Пароль** - вход по номеру телефона и паролю (альтернативный способ)

## Для пользователей

### Вход через WhatsApp (рекомендуется)

1. Откройте страницу входа
2. Выберите вкладку "WhatsApp"
3. Введите номер телефона в формате 77001234567
4. Нажмите "Отправить код"
5. Получите код в WhatsApp
6. Введите код и нажмите "Войти"

### Вход по паролю

1. Откройте страницу входа
2. Выберите вкладку "Пароль"
3. Введите номер телефона и пароль
4. Нажмите "Войти"

**Примечание:** Для входа по паролю необходимо сначала установить пароль в настройках профиля.

### Установка пароля

1. Войдите в систему через WhatsApp
2. Нажмите на иконку настроек (⚙️) в правом верхнем углу
3. Перейдите в раздел "Установить пароль"
4. Введите новый пароль (минимум 6 символов)
5. Подтвердите пароль
6. Нажмите "Установить пароль"

### Изменение пароля

1. Откройте настройки профиля
2. В разделе "Изменить пароль":
   - Введите текущий пароль
   - Введите новый пароль
   - Подтвердите новый пароль
3. Нажмите "Изменить пароль"

### Сброс пароля

Если вы забыли пароль:

1. На странице входа выберите вкладку "Пароль"
2. Нажмите "Забыли пароль?"
3. Введите номер телефона
4. Получите код подтверждения в WhatsApp
5. Введите код
6. Установите новый пароль

## API Endpoints

### WhatsApp OTP

#### Отправка OTP кода
```http
POST /api/auth/send-otp/
Content-Type: application/json

{
  "phone_number": "77001234567"
}
```

**Ответ:**
```json
{
  "message": "OTP код отправлен на WhatsApp",
  "phone_number": "77001234567"
}
```

#### Проверка OTP кода
```http
POST /api/auth/verify-otp/
Content-Type: application/json

{
  "phone_number": "77001234567",
  "code": "123456"
}
```

**Ответ:**
```json
{
  "user": {
    "id": 1,
    "phone_number": "77001234567",
    "phone_verified": true,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Авторизация по паролю

#### Вход по паролю
```http
POST /api/auth/login-password/
Content-Type: application/json

{
  "phone_number": "77001234567",
  "password": "mypassword123"
}
```

**Ответ:**
```json
{
  "user": {
    "id": 1,
    "phone_number": "77001234567",
    "phone_verified": true,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

#### Установка/изменение пароля
```http
POST /api/auth/set-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "new_password": "newpassword123",
  "current_password": "oldpassword123"  // Обязательно, если пароль уже установлен
}
```

**Ответ:**
```json
{
  "message": "Пароль успешно установлен",
  "has_password": true
}
```

#### Запрос на сброс пароля
```http
POST /api/auth/reset-password/request/
Content-Type: application/json

{
  "phone_number": "77001234567"
}
```

**Ответ:**
```json
{
  "message": "Код для сброса пароля отправлен на WhatsApp",
  "phone_number": "77001234567"
}
```

#### Подтверждение сброса пароля
```http
POST /api/auth/reset-password/confirm/
Content-Type: application/json

{
  "phone_number": "77001234567",
  "code": "123456",
  "new_password": "newpassword123"
}
```

**Ответ:**
```json
{
  "message": "Пароль успешно изменен"
}
```

### Профиль пользователя

```http
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "user": {
    "id": 1,
    "phone_number": "77001234567",
    "phone_verified": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "has_password": true
  },
  "roles": ["employer_owner"],
  "primary_role": "employer",
  "organizations": [...]
}
```

## Безопасность

### Требования к паролю
- Минимум 6 символов
- Хранится в зашифрованном виде (Django password hashing)

### OTP коды
- Действительны в течение времени, указанного в `OTP_EXPIRY_MINUTES` (по умолчанию 5 минут)
- Одноразовые (после использования помечаются как использованные)
- Отправляются через Green-API WhatsApp

### Токены JWT
- Access token - для доступа к API
- Refresh token - для обновления access token
- Хранятся в localStorage на клиенте

## Настройка

### Backend (.env)
```env
# Green-API для WhatsApp
GREEN_API_INSTANCE_ID=your_instance_id
GREEN_API_TOKEN=your_token

# OTP настройки
OTP_EXPIRY_MINUTES=5

# JWT настройки (в settings.py)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

### Frontend (.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Тестирование

### Тестирование WhatsApp OTP
```bash
# Отправка OTP
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "77001234567"}'

# Проверка OTP
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "77001234567", "code": "123456"}'
```

### Тестирование авторизации по паролю
```bash
# Установка пароля (требуется токен)
curl -X POST http://localhost:8000/api/auth/set-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"new_password": "password123"}'

# Вход по паролю
curl -X POST http://localhost:8000/api/auth/login-password/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "77001234567", "password": "password123"}'
```

## Миграции

После добавления функциональности паролей не требуется дополнительных миграций, так как модель User наследуется от AbstractUser, который уже содержит поле password.

## Troubleshooting

### Пользователь не может войти по паролю
- Проверьте, установлен ли пароль: `user.has_usable_password()`
- Убедитесь, что номер телефона нормализован правильно

### OTP код не приходит
- Проверьте настройки Green-API
- Убедитесь, что номер телефона зарегистрирован в WhatsApp
- Проверьте логи Django на наличие ошибок

### Токен истек
- Используйте refresh token для получения нового access token
- Или войдите заново

## Дальнейшие улучшения

Возможные улучшения системы авторизации:

1. **2FA (двухфакторная аутентификация)** - обязательный OTP даже при входе по паролю
2. **Биометрия** - вход по отпечатку пальца/Face ID на мобильных устройствах
3. **История входов** - логирование всех попыток входа
4. **Блокировка после неудачных попыток** - защита от брутфорса
5. **Email как альтернатива** - возможность привязать email для восстановления
6. **Сессии** - управление активными сессиями пользователя
