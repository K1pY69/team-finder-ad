import json
from pathlib import Path

from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User

DEFAULT_DATA_FILE = Path(__file__).parent / "test_data.json"


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей, навыки и проекты"

    def add_arguments(self, parser):
        parser.add_argument(
            "--data",
            type=Path,
            default=DEFAULT_DATA_FILE,
            help="Путь к JSON-файлу с тестовыми данными",
        )

    def handle(self, *args, **options):
        with open(options["data"], encoding="utf-8") as f:
            data = json.load(f)

        skills_list = data["skills"]
        users_list = data["users"]
        projects_list = data["projects"]
        participants_list = data["project_participants"]

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
        for skill_name in skills_list:
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            skill_objs[skill_name] = skill
        self.stdout.write(f"  Навыки готовы: {', '.join(skills_list)}")

        user_objs = {}
        for user_data in users_list:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "name": user_data["name"],
                    "surname": user_data["surname"],
                    "phone": user_data.get("phone", ""),
                    "github_url": user_data.get("github_url", ""),
                    "about": user_data.get("about", ""),
                },
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(f"  Создан пользователь: {user.email}")
            else:
                self.stdout.write(f"  Уже существует: {user.email}")
            for skill_name in user_data.get("skills", []):
                user.skills.add(skill_objs[skill_name])
            user_objs[user_data["email"]] = user

        project_objs = {}
        for project_data in projects_list:
            owner = user_objs.get(project_data["owner_email"])
            if not owner:
                msg = f"  Владелец не найден: {project_data['owner_email']}"
                self.stdout.write(self.style.WARNING(msg))
                continue
            project, created = Project.objects.get_or_create(
                name=project_data["name"],
                owner=owner,
                defaults={
                    "description": project_data["description"],
                    "github_url": project_data["github_url"],
                    "status": project_data["status"],
                },
            )
            if created:
                project.participants.add(owner)
                for skill_name in project_data.get("skills", []):
                    project.skills.add(skill_objs[skill_name])
                self.stdout.write(f"  Создан проект: {project.name}")
            else:
                self.stdout.write(f"  Уже существует: {project.name}")
            project_objs[project_data["name"]] = project

        for project_name, participant_email in participants_list:
            project = project_objs.get(project_name)
            participant = user_objs.get(participant_email)
            if project and participant:
                project.participants.add(participant)

        self.stdout.write(self.style.SUCCESS("Тестовые данные созданы!"))
