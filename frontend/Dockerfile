FROM node:18-alpine

WORKDIR /app

# Копирование package файлов
COPY package*.json ./

# Установка зависимостей
RUN npm install

# Копирование проекта
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

