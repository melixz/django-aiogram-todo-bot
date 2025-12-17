# django-aiogram-todo-bot

Сервис управления списком задач (ToDo List) с Telegram-ботом, Django REST API, Celery и Docker.

## Особенности

- **Django & DRF**: REST API для задач и категорий, админ-панель.
- **Aiogram 3**: Асинхронный Telegram-бот с интерактивными диалогами (aiogram-dialog).
- **Celery & Redis**: Отправка уведомлений о дедлайнах задач в Telegram.
- **ULID**: Использование ULID в качестве Primary Key (вместо UUID/int).
- **PostgreSQL**: Надежное хранение данных.
- **Часовой пояс**: Настроен на `America/Adak`.

## Быстрый старт

### Требования

- Docker и Docker Compose
- Telegram Bot Token (от @BotFather)

### Запуск через Docker

1. Создайте файл `.env` в корне проекта (используйте `env.example` как шаблон):
   ```bash
   cp env.example .env
   ```
   Впишите свой `TELEGRAM_BOT_TOKEN`.

2. Запустите проект:
   ```bash
   docker-compose up --build
   ```

При старте автоматически выполняются:
- Миграции базы данных
- Сбор статических файлов
- Создание администратора (логин: `admin`, пароль: `admin`)

После старта:
- **Bot**: Напишите `/start` своему боту в Telegram.
- **Admin Panel**: `http://localhost:8000/admin/` (логин: `admin`, пароль: `admin`)
- **API**: `http://localhost:8000/api/v1/`

### Локальный запуск (для разработки)

При наличии локальных PostgreSQL и Redis:

**Backend:**
```bash
cd backend
uv pip install -r pyproject.toml
python manage.py migrate
python manage.py createadmin
python manage.py runserver
```

**Bot:**
```bash
cd bot
uv pip install -r pyproject.toml
python main.py
```

## Административный интерфейс

Админ-панель Django доступна по адресу `http://localhost:8000/admin/` и позволяет управлять задачами и категориями всех пользователей. Суперпользователь создается автоматически при первом запуске контейнера `backend` (логин: `admin`, пароль: `admin`). Для продакшена рекомендуется изменить пароль после первого входа.

## Структура проекта

```text
django-aiogram-todo-bot/
├── backend/                 # Django проект
│   ├── api/                 # DRF API (v1)
│   ├── config/              # Настройки проекта (settings, urls, celery)
│   ├── core/                # Базовые модели (BaseModel с ULID)
│   │   └── management/      # Management команды (createadmin)
│   ├── categories/          # Приложение категорий
│   ├── tasks/               # Приложение задач и Celery таски
│   ├── Dockerfile           # Docker config для backend/celery
│   ├── entrypoint.sh        # Скрипт запуска (миграции + статика + админ)
│   └── pyproject.toml       # Зависимости backend
├── bot/                     # Aiogram бот
│   ├── dialogs/             # Диалоги (aiogram-dialog)
│   ├── handlers.py          # Обработчики команд
│   ├── api_client.py        # Клиент к Django API
│   ├── main.py              # Точка входа
│   ├── Dockerfile           # Docker config для бота
│   └── pyproject.toml       # Зависимости бота
├── docker-compose.yml       # Оркестрация сервисов
├── env.example              # Пример переменных окружения
└── README.md                # Документация
```

## API Эндпоинты

Все запросы требуют заголовок `X-Telegram-ID` для идентификации пользователя.

### Задачи (`/api/v1/tasks/`)
- `GET /` — Список задач.
- `POST /` — Создать задачу.
- `GET /{id}/` — Детали задачи.
- `PATCH /{id}/` — Обновить задачу (в т.ч. завершить).
- `DELETE /{id}/` — Удалить задачу.

### Категории (`/api/v1/categories/`)
- `GET /` — Список категорий.
- `POST /` — Создать категорию.

## Функционал бота

- **Просмотр задач**: Список с иконками статуса.
- **Детали задачи**: Статус, категория, срок, дата создания (в формате ДД.ММ.ГГГГ ЧЧ:ММ).
- **Управление**: Завершение и удаление задач.
- **Создание**:
  - Ввод названия.
  - Ввод описания (можно пропустить).
  - Выбор категории (или создание новой).
  - Установка срока (парсинг форматов даты).
