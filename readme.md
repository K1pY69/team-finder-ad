# TeamFinder

TeamFinder — платформа для поиска участников в pet-проекты. Разработчики, дизайнеры и другие специалисты публикуют идеи, находят команду и откликаются на интересные проекты.

Реализован **Вариант 2**: навыки пользователей + фильтрация участников по навыку.

## Функциональность

- Регистрация и вход по email/паролю (после регистрации пользователь автоматически авторизуется)
- Профиль пользователя: имя, аватар, «о себе», контакты (email, телефон, GitHub), навыки
- Список участников с фильтрацией по навыку
- Создание, редактирование и завершение проектов
- Присоединение к открытым проектам / выход из них
- Управление навыками профиля и проекта с автодополнением (без перезагрузки страницы)
- Пагинация на главной (12 проектов на странице) и на списке пользователей (12 на странице)
- Автогенерация аватара при регистрации (первая буква имени на пастельном фоне)
- Валидация телефона (`8XXXXXXXXXX` или `+7XXXXXXXXXX`) и ссылки на GitHub

## Стек

- Python 3.12 / Django 5.2
- PostgreSQL 16
- Docker Compose
- Pillow — генерация аватаров

## Запуск через Docker (рекомендуется)

```bash
cp .env_example .env
docker compose up -d --build
docker compose exec web python manage.py create_test_data
```

Открыть: http://127.0.0.1:8000

При старте контейнер `web` сам применяет миграции и собирает статику.

## Локальный запуск (без Docker)

```bash
# 1. Создайте БД team_finder в PostgreSQL
# 2. Скопируйте конфиг и укажите POSTGRES_HOST=localhost, актуальный POSTGRES_PORT
cp .env_example .env

pip install -r requirements.txt
python manage.py migrate
python manage.py create_test_data
python manage.py runserver
```

## Полезные команды

```bash
# Логи web-контейнера
docker compose logs -f web

# Шелл внутри контейнера
docker compose exec web bash

# Тесты
docker compose exec web python manage.py test

# Создать суперпользователя руками
docker compose exec web python manage.py createsuperuser

# Остановить
docker compose down

# Остановить и очистить данные БД (полный сброс)
docker compose down -v
```

## Тестовые аккаунты

После выполнения `create_test_data`:

| Имя | Email | Пароль | Роль |
|---|---|---|---|
| — | admin@example.com | admin123 | Администратор |
| Мария Захарова | maria.zakharova@mail.ru | qwerty2024 | Backend (Python, Django) |
| Алексей Воронов | alex.voronov@gmail.com | qwerty2024 | Fullstack (Django, React) |
| Екатерина Новикова | kate.novikova@yandex.ru | qwerty2024 | DevOps (Docker, Kubernetes) |
| Сергей Белов | s.belov@inbox.ru | qwerty2024 | Python-разработчик |

## Тестовые проекты

| Проект | Автор | Статус |
|---|---|---|
| CodeReview Bot | Мария Захарова | Открыт |
| Habit Tracker API | Мария Захарова | Открыт |
| DevDashboard | Алексей Воронов | Открыт |
| Open Recipe Book | Алексей Воронов | Закрыт |
| K8s Local Cluster | Екатерина Новикова | Открыт |
| DB Migration CLI | Сергей Белов | Открыт |
| Log Aggregator | Сергей Белов | Закрыт |

## Структура

- `team_finder/` — настройки проекта, корневой `urls.py`, общие миксины и сервисы
- `users/` — приложение пользователей: модель `User` (кастомная, `USERNAME_FIELD = email`), модель `Skill`, формы регистрации/входа/редактирования профиля/смены пароля, автогенерация аватара
- `projects/` — приложение проектов: модель `Project`, формы, представления, переключение участия и статуса
- `templates_var2/` — HTML-шаблоны для Варианта 2
- `static/` — CSS, JS, шрифты, картинки

## Автор

**Карпов Вадим** — thekvm@yandex.ru
