FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание директорий для статики и медиа
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

