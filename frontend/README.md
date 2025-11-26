# ProfMed.kz Frontend

Современный фронтенд для платформы автоматизации медицинских осмотров.

## Технологии

- **Next.js 14** - React фреймворк с App Router
- **TypeScript** - Типизированный JavaScript
- **Tailwind CSS** - Utility-first CSS фреймворк
- **Zustand** - Легковесное управление состоянием
- **Axios** - HTTP клиент
- **Lucide React** - Иконки

## Структура проекта

```
frontend/
├── app/                    # Next.js App Router
│   ├── login/             # Страница авторизации
│   ├── dashboard/         # Главная панель управления
│   └── layout.tsx         # Корневой layout
├── components/            # React компоненты
│   └── ui/               # UI компоненты (Button, Input, Card)
├── lib/                  # Утилиты и API клиент
├── store/                # Zustand stores
└── middleware.ts         # Next.js middleware
```

## Запуск

```bash
# Установка зависимостей
npm install

# Разработка
npm run dev

# Сборка для продакшена
npm run build
npm start
```

## Основные страницы

- `/login` - Авторизация через WhatsApp OTP
- `/dashboard` - Главная панель управления
- `/dashboard/organizations` - Управление организациями
- `/dashboard/calendar` - Календарь осмотров
- `/dashboard/documents` - Генерация документов

## API Интеграция

Все API запросы идут через `lib/api.ts` с автоматической добавкой JWT токенов.

## Дизайн система

Используется Tailwind CSS с кастомной цветовой палитрой:
- Primary: Синий (#0ea5e9)
- Success: Зеленый
- Error: Красный
- Gray: Нейтральные оттенки

