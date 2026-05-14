from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User


SKILLS = [
    "Python",
    "Django",
    "JavaScript",
    "React",
    "Docker",
    "PostgreSQL",
    "Git",
    "Kubernetes",
    "FastAPI",
    "TypeScript",
]

USERS = [
    {
        "email": "maria.zakharova@mail.ru",
        "name": "Мария",
        "surname": "Захарова",
        "password": "qwerty2024",
        "phone": "+79161234567",
        "github_url": "https://github.com/mzakharova",
        "about": (
            "Backend-разработчик с 4 годами опыта на Python и Django. "
            "Люблю чистую архитектуру и автотесты. "
            "В свободное время пишу pet-проекты и читаю про distributed systems."
        ),
        "skills": ["Python", "Django", "PostgreSQL", "FastAPI"],
    },
    {
        "email": "alex.voronov@gmail.com",
        "name": "Алексей",
        "surname": "Воронов",
        "password": "qwerty2024",
        "phone": "+79037654321",
        "github_url": "https://github.com/alexvoronov",
        "about": (
            "Fullstack-разработчик. Пишу на Django и React, иногда на TypeScript. "
            "Интересуюсь UX и стараюсь делать интерфейсы удобными для людей, "
            "а не только для разработчиков."
        ),
        "skills": ["Python", "Django", "JavaScript", "React", "TypeScript", "Git"],
    },
    {
        "email": "kate.novikova@yandex.ru",
        "name": "Екатерина",
        "surname": "Новикова",
        "password": "qwerty2024",
        "phone": "+79265550099",
        "github_url": "https://github.com/knovikova",
        "about": (
            "DevOps-инженер. Занимаюсь CI/CD, контейнеризацией и мониторингом. "
            "Убеждена, что хорошая инфраструктура — это когда о ней никто не думает."
        ),
        "skills": ["Docker", "Kubernetes", "PostgreSQL", "Git"],
    },
    {
        "email": "s.belov@inbox.ru",
        "name": "Сергей",
        "surname": "Белов",
        "password": "qwerty2024",
        "phone": "+79991112233",
        "github_url": "https://github.com/sergeybelov",
        "about": (
            "Python-разработчик, пишу инструменты и утилиты для автоматизации. "
            "Фанат CLI-инструментов и хорошей документации. "
            "Открыт к новым проектам и идеям."
        ),
        "skills": ["Python", "Django", "Docker", "Git", "PostgreSQL"],
    },
]

PROJECTS = [
    {
        "owner_email": "maria.zakharova@mail.ru",
        "name": "CodeReview Bot",
        "description": (
            "Телеграм-бот, который автоматически проверяет Pull Request на GitHub "
            "с помощью GPT. Бот получает diff PR, анализирует код на ошибки и стиль, "
            "оставляет комментарии прямо в PR. "
            "Цель — снизить нагрузку на ревьюеров и ускорить обратную связь.\n\n"
            "Ищем: backend-разработчика с опытом работы с GitHub API и ботами."
        ),
        "github_url": "",
        "status": "open",
        "skills": ["Python", "FastAPI", "Git"],
    },
    {
        "owner_email": "maria.zakharova@mail.ru",
        "name": "Habit Tracker API",
        "description": (
            "REST API для трекинга привычек: добавление, отметка выполнения, статистика. "
            "Планируется интеграция с Telegram для ежедневных напоминаний. "
            "Пишем на Django REST Framework, данные храним в PostgreSQL.\n\n"
            "Ищем: frontend-разработчика для создания интерфейса на React."
        ),
        "github_url": "",
        "status": "open",
        "skills": ["Python", "Django", "PostgreSQL"],
    },
    {
        "owner_email": "alex.voronov@gmail.com",
        "name": "DevDashboard",
        "description": (
            "Персональный дашборд для разработчика: GitHub PR, задачи и метрики "
            "в одном окне. Поддержка тёмной темы, виджеты настраиваются перетаскиванием.\n\n"
            "Стек: Django (бэкенд) + React + TypeScript (фронтенд). "
            "Ищем: TypeScript-разработчика с опытом React."
        ),
        "github_url": "",
        "status": "open",
        "skills": ["Python", "Django", "React", "TypeScript"],
    },
    {
        "owner_email": "alex.voronov@gmail.com",
        "name": "Open Recipe Book",
        "description": (
            "Коллаборативная книга рецептов с поиском по ингредиентам и рейтингом. "
            "Пользователи добавляют рецепты, комментируют и сохраняют понравившиеся. "
            "Проект завершён — MVP выпущен."
        ),
        "github_url": "",
        "status": "closed",
        "skills": ["Python", "Django", "JavaScript", "PostgreSQL"],
    },
    {
        "owner_email": "kate.novikova@yandex.ru",
        "name": "K8s Local Cluster",
        "description": (
            "Набор скриптов, Helm-чартов и документации для быстрого развёртывания "
            "локального Kubernetes-кластера на ноутбуке (minikube / kind). "
            "Включает мониторинг (Prometheus + Grafana) и примеры деплоя.\n\n"
            "Ищем: разработчиков для изучения Kubernetes на практике."
        ),
        "github_url": "",
        "status": "open",
        "skills": ["Docker", "Kubernetes", "Git"],
    },
    {
        "owner_email": "s.belov@inbox.ru",
        "name": "DB Migration CLI",
        "description": (
            "Утилита для безопасного переноса данных между разными СУБД "
            "(PostgreSQL, MySQL, SQLite). Поддерживает маппинг типов, dry-run и логи. "
            "Написана на Python, распространяется как pip-пакет.\n\n"
            "Ищем: разработчика с опытом SQLAlchemy или БД драйверов."
        ),
        "github_url": "",
        "status": "open",
        "skills": ["Python", "PostgreSQL", "Git"],
    },
    {
        "owner_email": "s.belov@inbox.ru",
        "name": "Log Aggregator",
        "description": (
            "Лёгкий агрегатор логов: собирает из файлов и stdin, "
            "фильтрует по уровню и паттернам, экспортирует в CSV и JSON. "
            "Используется в pet-проектах как зависимость."
        ),
        "github_url": "",
        "status": "closed",
        "skills": ["Python", "Docker"],
    },
]

PROJECT_PARTICIPANTS = [
    ("CodeReview Bot", "alex.voronov@gmail.com"),
    ("DevDashboard", "kate.novikova@yandex.ru"),
    ("K8s Local Cluster", "s.belov@inbox.ru"),
]


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей, навыки и проекты"

    def handle(self, *args, **options):
        self.stdout.write("Создание тестовых данных...")

        admin, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "name": "Admin",
                "surname": "Super",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(f"  Создан суперюзер: {admin.email}")
        else:
            self.stdout.write(f"  Уже существует: {admin.email}")

        skill_objs = {}
        for skill_name in SKILLS:
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            skill_objs[skill_name] = skill
        self.stdout.write(f"  Навыки готовы: {', '.join(SKILLS)}")

        user_objs = {}
        for data in USERS:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "surname": data["surname"],
                    "phone": data.get("phone", ""),
                    "github_url": data.get("github_url", ""),
                    "about": data.get("about", ""),
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(f"  Создан пользователь: {user.email}")
            else:
                self.stdout.write(f"  Уже существует: {user.email}")
            for skill_name in data.get("skills", []):
                user.skills.add(skill_objs[skill_name])
            user_objs[data["email"]] = user

        project_objs = {}
        for data in PROJECTS:
            owner = user_objs.get(data["owner_email"])
            if not owner:
                msg = f"  Владелец не найден: {data['owner_email']}"
                self.stdout.write(self.style.WARNING(msg))
                continue
            project, created = Project.objects.get_or_create(
                name=data["name"],
                owner=owner,
                defaults={
                    "description": data["description"],
                    "github_url": data["github_url"],
                    "status": data["status"],
                },
            )
            if created:
                project.participants.add(owner)
                for skill_name in data.get("skills", []):
                    project.skills.add(skill_objs[skill_name])
                self.stdout.write(f"  Создан проект: {project.name}")
            else:
                self.stdout.write(f"  Уже существует: {project.name}")
            project_objs[data["name"]] = project

        for project_name, participant_email in PROJECT_PARTICIPANTS:
            project = project_objs.get(project_name)
            participant = user_objs.get(participant_email)
            if project and participant:
                project.participants.add(participant)

        self.stdout.write(self.style.SUCCESS("Тестовые данные созданы!"))
