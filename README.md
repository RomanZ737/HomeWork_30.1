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

**CI/CD и автоматический деплой**
Проект настроен на непрерывную интеграцию и доставку с помощью **GitHub Actions**.

Как работает pipeline

Workflow запускается при каждом push в ветку main. Он состоит из четырёх этапов:
* **lint** – проверка кода с помощью flake8.
* **test** – запуск тестов Django с использованием PostgreSQL и Redis (поднимаются как сервисы в GitHub Actions).
* **build** – сборка Docker-образа и публикация его в Docker Hub.
* **deploy** – подключение к удалённому серверу по SSH, копирование файлов (docker-compose.yml, nginx.conf, html/) и запуск контейнеров через Docker Compose.


**Необходимые секреты GitHub**

Для работы pipeline в репозитории должны быть настроены следующие секреты (Settings → Secrets and variables → Actions):
**Секрет	                Описание**
SECRET_KEY	            *Секретный ключ Django (используется в тестах).*
DOCKER_HUB_USERNAME	    *Имя пользователя Docker Hub.*
DOCKER_HUB_ACCESS_TOKEN	*Токен доступа Docker Hub (можно создать в настройках Docker Hub).*
SSH_KEY	                *Приватный SSH-ключ для доступа к серверу.*
SSH_USER	            *Имя пользователя на сервере (например, roman).*
SERVER_IP	            *IP-адрес удалённого сервера.*
DEPLOY_DIR	            *Абсолютный путь к директории на сервере (например, /var/www/lms).*


**Подготовка удалённого сервера**

- Установите Docker и Docker Compose v2:

bash

    sudo apt update
    sudo apt install docker.io docker-compose-plugin -y
    sudo usermod -aG docker $USER   # добавьте пользователя SSH в группу docker

- Создайте директорию для проекта (если ещё не создана):

bash

    sudo mkdir -p /var/www/lms
    sudo chown $USER:$USER /var/www/lms

- Создайте файл .env в /var/www/lms с реальными переменными окружения.
    Пример можно взять из .env.example (только не забудьте указать POSTGRES_HOST=db, REDIS_HOST=redis).

bash

    cd /var/www/lms
    nano .env