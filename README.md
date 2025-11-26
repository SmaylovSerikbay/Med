# ProfMed.kz (131.Flow)
## Цифровая экосистема обязательных медицинских осмотров РК

Платформа для автоматизации процесса обязательных медосмотров согласно **Приказу МЗ РК № ҚР ДСМ-131/2020**.

### Технологический стек

- **Backend:** Django REST Framework + PostgreSQL
- **Frontend:** Next.js (React)
- **Авторизация:** WhatsApp OTP через Green-API
- **Инфраструктура:** Docker Compose

### Быстрый старт

```bash
# Клонировать репозиторий
git clone <repo-url>
cd Med

# Запустить через Docker Compose
docker-compose up -d

# Применить миграции
docker-compose exec backend python manage.py migrate

# Создать суперпользователя
docker-compose exec backend python manage.py createsuperuser
```

### Структура проекта

```
Med/
├── backend/          # Django REST API
├── frontend/         # Next.js приложение
├── docker-compose.yml
└── README.md
```

### Переменные окружения

Создайте файлы `.env` в `backend/` и `frontend/` (см. `.env.example`)

### Документация

Подробное описание видения продукта: [VISION.md](./VISION.md)

