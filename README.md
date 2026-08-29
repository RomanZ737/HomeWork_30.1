# LMS Backend API

Бэкенд-сервер для LMS-системы (Learning Management System), предоставляющий REST API для онлайн-обучения. Проект реализован как SPA-совместимый backend, возвращающий данные в формате JSON.

## Технологический стек

- **Python 3.13**
- **Django 6.0**
- **Django REST Framework**
- **PostgreSQL 16** (в Docker)
- **Redis 7** (кэширование, Celery)
- **Celery + Celery Beat** (асинхронные задачи)
- **SimpleJWT** (аутентификация по JWT)
- **drf-yasg** (документация API)
- **Docker, Docker Compose**

## Функциональность

- Пользователи и аутентификация (JWT)
- Управление курсами и учебными материалами
- Подписки и платежи (Stripe)
- Отправка email-уведомлений
- Периодические задачи (Celery Beat) для проверки активности пользователей
- Кэширование часто запрашиваемых данных через Redis

## Структура проекта
├── config/ # Основные настройки Django
├── users/ # Пользовательская модель, регистрация, аутентификация
├── lms/ # Основное приложение: курсы, уроки, материалы
├── Dockerfile
├── docker-compose.yml
├── .env # Переменные окружения (не коммитить!)
├── requirements.txt
└── manage.py


## Запуск с использованием Docker


1. **Клонируйте репозиторий:**

   ```bash
   git clone <url-репозитория>

2. Создайте файл .env из файла .env.example 

3. Соберите и запустите контейнеры:
   - docker-compose up --build
4. После успешного запуска:
    - Backend API будет доступен по адресу: http://localhost:8000/api/

    - Документация Swagger: http://localhost:8000/swagger/

    - Документация ReDoc: http://localhost:8000/redoc/
5. Примените миграции
    - docker-compose exec web python manage.py migrate
    - docker-compose exec web python manage.py createsuperuser
6. Запустите Celery worker и beat
    - docker-compose exec web celery -A config worker -l info
    - docker-compose exec web celery -A config beat -l info

# В файле docker-compose.yml описаны три сервиса:
    db – PostgreSQL 16, данные сохраняются в volume postgres_data.

    redis – Redis 7, данные в volume redis_data.

    web – Django-приложение, собирается из Dockerfile, порт 8000.

# Запуск контейнеров одной командой
    docker-compose up -d

# docker-compose down
    docker-compose down

# Основные эндпоинты
    POST /api/token/ – получение JWT-токена

    POST /api/token/refresh/ – обновление токена

    GET /api/users/ – список пользователей (требует аутентификации)

    GET /api/courses/ – список курсов

    POST /api/courses/ – создание курса (только для преподавателей)