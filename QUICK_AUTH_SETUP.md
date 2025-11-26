# Быстрая настройка авторизации

## Что добавлено

✅ Вход по паролю в дополнение к WhatsApp OTP
✅ Установка/изменение пароля в настройках профиля
✅ Сброс пароля через WhatsApp
✅ Переключатель между методами входа на странице логина

## Запуск

### 1. Backend

Миграции не требуются (поле password уже есть в AbstractUser).

Запустите сервер:
```bash
cd backend
python manage.py runserver
```

### 2. Frontend

Установите зависимости (если еще не установлены):
```bash
cd frontend
npm install
```

Запустите dev сервер:
```bash
npm run dev
```

## Использование

### Для пользователей

1. **Первый вход** - через WhatsApp OTP (как обычно)
2. **Установка пароля** - в настройках профиля (иконка ⚙️)
3. **Вход по паролю** - выберите вкладку "Пароль" на странице входа

### Для разработчиков

#### Новые API endpoints:

```python
# Вход по паролю
POST /api/auth/login-password/
{
  "phone_number": "77001234567",
  "password": "mypassword"
}

# Установка пароля
POST /api/auth/set-password/
{
  "new_password": "newpassword",
  "current_password": "oldpassword"  # если пароль уже установлен
}

# Сброс пароля - запрос
POST /api/auth/reset-password/request/
{
  "phone_number": "77001234567"
}

# Сброс пароля - подтверждение
POST /api/auth/reset-password/confirm/
{
  "phone_number": "77001234567",
  "code": "123456",
  "new_password": "newpassword"
}
```

#### Новые frontend страницы:

- `/login` - обновлена с переключателем методов
- `/dashboard/settings` - новая страница настроек

#### Обновленные компоненты:

- `Header.tsx` - добавлена кнопка настроек
- `authStore.ts` - без изменений
- `userStore.ts` - добавлено поле `has_password`
- `api.ts` - добавлены новые методы API

## Тестирование

### Сценарий 1: Установка пароля

1. Войдите через WhatsApp OTP
2. Откройте настройки (⚙️)
3. Установите пароль
4. Выйдите
5. Войдите по паролю

### Сценарий 2: Сброс пароля

1. На странице входа выберите "Пароль"
2. Нажмите "Забыли пароль?"
3. Введите номер телефона
4. Получите код в WhatsApp
5. Установите новый пароль
6. Войдите с новым паролем

## Файлы изменений

### Backend
- `backend/apps/authentication/views.py` - добавлены 4 новых view
- `backend/apps/authentication/urls.py` - добавлены 4 новых URL
- `backend/apps/authentication/serializers.py` - добавлены 4 новых serializer

### Frontend
- `frontend/app/login/page.tsx` - обновлена страница входа
- `frontend/app/dashboard/settings/page.tsx` - новая страница настроек
- `frontend/components/layout/Header.tsx` - добавлена кнопка настроек
- `frontend/lib/api.ts` - добавлены новые API методы
- `frontend/store/userStore.ts` - добавлено поле has_password

## Безопасность

- Пароли хешируются Django (PBKDF2)
- Минимальная длина пароля: 6 символов
- OTP коды для сброса пароля действительны 5 минут
- Требуется текущий пароль для изменения

## Поддержка

Полная документация: `AUTHENTICATION_GUIDE.md`
