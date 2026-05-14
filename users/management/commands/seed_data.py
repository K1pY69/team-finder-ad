from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User


SKILLS = [
    "Python",
    "Django",
    "React",
    "TypeScript",
    "PostgreSQL",
    "Docker",
    "FastAPI",
    "Go",
]

USERS = [
    {
        "email": "maria@yandex.ru",
        "name": "Мария",
        "surname": "Иванова",
        "password": "password",
        "about": "Fullstack-разработчик",
        "phone": "+71234567890",
        "skills": ["Python", "Django", "React"],
    },
    {
        "email": "ivan@example.com",
        "name": "Иван",
        "surname": "Петров",
        "password": "password",
        "about": "Backend-разработчик на Go",
        "phone": "+71234567891",
        "skills": ["Go", "Docker", "PostgreSQL"],
    },
    {
        "email": "anna@example.com",
        "name": "Анна",
        "surname": "Сидорова",
        "password": "password",
        "about": "Frontend-разработчик",
        "phone": "+71234567892",
        "skills": ["React", "TypeScript"],
    },
    {
        "email": "alex@example.com",
        "name": "Алексей",
        "surname": "Козлов",
        "password": "password",
        "about": "DevOps-инженер",
        "phone": "+71234567893",
        "skills": ["Docker", "PostgreSQL", "Python"],
    },
    {
        "email": "kate@example.com",
        "name": "Екатерина",
        "surname": "Новикова",
        "password": "password",
        "about": "Python-разработчик",
        "phone": "+71234567894",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
    },
]

PROJECTS = [
    {
        "owner_email": "maria@yandex.ru",
        "name": "TaskFlow — менеджер задач",
        "description": (
            "Веб-приложение для управления задачами команды с канбан-доской."
        ),
        "status": "open",
    },
    {
        "owner_email": "maria@yandex.ru",
        "name": "Читалка книг",
        "description": (
            "Мобильное приложение для чтения и хранения заметок по книгам."
        ),
        "status": "open",
    },
    {
        "owner_email": "ivan@example.com",
        "name": "OpenWeather Bot",
        "description": (
            "Telegram-бот для мониторинга погоды с оповещениями."
        ),
        "status": "open",
    },
    {
        "owner_email": "anna@example.com",
        "name": "Portfolio Constructor",
        "description": (
            "Генератор портфолио для разработчиков на основе GitHub."
        ),
        "status": "open",
    },
    {
        "owner_email": "alex@example.com",
        "name": "Deploy Dashboard",
        "description": (
            "Дашборд для мониторинга деплоев и статуса сервисов."
        ),
        "status": "closed",
    },
    {
        "owner_email": "kate@example.com",
        "name": "Recipe API",
        "description": (
            "REST API для хранения и поиска рецептов с рейтингом."
        ),
        "status": "open",
    },
]


class Command(BaseCommand):
    help = "Seed database with test users, skills and projects"

    def handle(self, *args, **options):
        self.stdout.write("Creating skills...")
        skill_objs = {}
        for name in SKILLS:
            skill, _ = Skill.objects.get_or_create(name=name)
            skill_objs[name] = skill

        self.stdout.write("Creating users...")
        user_objs = {}
        for data in USERS:
            if User.objects.filter(email=data["email"]).exists():
                user_objs[data["email"]] = User.objects.get(email=data["email"])
                self.stdout.write(f"  skip (exists): {data['email']}")
                continue
            user = User.objects.create_user(
                email=data["email"],
                name=data["name"],
                surname=data["surname"],
                password=data["password"],
                about=data.get("about", ""),
                phone=data.get("phone", ""),
            )
            for sname in data.get("skills", []):
                user.skills.add(skill_objs[sname])
            user_objs[data["email"]] = user
            self.stdout.write(f"  created: {user}")

        self.stdout.write("Creating projects...")
        for data in PROJECTS:
            owner = user_objs.get(data["owner_email"])
            if not owner:
                continue
            if Project.objects.filter(name=data["name"], owner=owner).exists():
                self.stdout.write(f"  skip (exists): {data['name']}")
                continue
            project = Project.objects.create(
                name=data["name"],
                description=data["description"],
                status=data["status"],
                owner=owner,
            )
            project.participants.add(owner)
            self.stdout.write(f"  created: {project}")

        self.stdout.write(self.style.SUCCESS("Done!"))
