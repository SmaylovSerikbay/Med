# Настройка переменных окружения для Backend

Создайте файл `.env` в директории `backend/` со следующим содержимым:

```env
# Django Settings
SECRET_KEY=ваш-секретный-ключ-здесь-сгенерируйте-случайный
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database
DB_NAME=profmed_db
DB_USER=profmed_user
DB_PASSWORD=profmed_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Green-API (WhatsApp OTP)
GREEN_API_ID_INSTANCE=7105394320
GREEN_API_TOKEN=6184c77e6f374ddc8003957d0d3f4ccc7bc1581c600847d889
GREEN_API_URL=https://7105.api.green-api.com

# JWT Settings
JWT_SECRET_KEY=ваш-jwt-секретный-ключ
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=86400

# OTP Settings
OTP_CODE_LENGTH=6
OTP_EXPIRY_MINUTES=5
```

## Генерация SECRET_KEY

Для генерации безопасного SECRET_KEY выполните:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Или используйте онлайн генератор Django secret key.

