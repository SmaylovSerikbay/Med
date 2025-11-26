# Инструкция по запуску ProfMed.kz

## Предварительные требования

- Docker и Docker Compose установлены
- Git

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Перейти в директорию проекта
cd Med

# Создать файл .env для backend
cp backend/.env.example backend/.env

# Отредактировать backend/.env и добавить:
# - SECRET_KEY (сгенерируйте случайный ключ)
# - GREEN_API_ID_INSTANCE=7105394320
# - GREEN_API_TOKEN=6184c77e6f374ddc8003957d0d3f4ccc7bc1581c600847d889
# - GREEN_API_URL=https://7105.api.green-api.com

# Создать файл .env для frontend
cp frontend/.env.example frontend/.env
```

### 2. Запуск через Docker Compose

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотреть логи
docker-compose logs -f backend
```

### 3. Инициализация базы данных

```bash
# Применить миграции
docker-compose exec backend python manage.py migrate

# Создать суперпользователя (опционально)
docker-compose exec backend python manage.py createsuperuser

# Загрузить начальные данные (планы подписок, вредные факторы)
# TODO: Создать команду для загрузки данных из Приказа 131
```

### 4. Доступ к приложению

- **Backend API:** http://localhost:8000/api/
- **Admin панель:** http://localhost:8000/admin/
- **Frontend:** http://localhost:3000/

## Разработка без Docker

### Backend (Django)

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Запустить сервер
python manage.py runserver
```

### Frontend (Next.js)

```bash
cd frontend

# Установить зависимости
npm install

# Запустить dev сервер
npm run dev
```

## Структура проекта

```
Med/
├── backend/                 # Django REST API
│   ├── apps/
│   │   ├── authentication/  # Авторизация через WhatsApp OTP
│   │   ├── subscriptions/  # Система подписок
│   │   ├── compliance/     # Логика Приказа 131
│   │   ├── organizations/  # Работодатели и Клиники
│   │   └── medical_examinations/  # Медосмотры
│   ├── config/             # Настройки Django
│   └── manage.py
├── frontend/               # Next.js приложение
│   ├── app/               # App Router (Next.js 14)
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Авторизация

- `POST /api/auth/send-otp/` - Отправка OTP кода на WhatsApp
- `POST /api/auth/verify-otp/` - Проверка OTP и получение JWT токенов
- `GET /api/auth/profile/` - Профиль текущего пользователя

### Подписки

- `GET /api/subscriptions/plans/` - Список планов подписки
- `GET /api/subscriptions/` - Мои подписки
- `GET /api/subscriptions/current/` - Текущая активная подписка

## Следующие шаги

1. ✅ Базовая структура проекта создана
2. ✅ Авторизация через WhatsApp OTP реализована
3. ✅ Система подписок создана
4. ⏳ Загрузка данных из Приказа 131 (вредные факторы, профессии)
5. ⏳ Реализация модуля Compliance (генерация списков, актов)
6. ⏳ Frontend интерфейсы для HR и Клиник

