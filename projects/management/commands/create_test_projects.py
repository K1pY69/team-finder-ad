import json
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from projects.models import Project

DEFAULT_JSON = os.path.join(os.path.dirname(__file__), "test_projects.json")


class Command(BaseCommand):
    help = "Create test projects with their relationships"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreate projects even if they exist",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Create projects only for specific username",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all existing projects before creating",
        )
        parser.add_argument(
            "--file",
            type=str,
            default=DEFAULT_JSON,
            help="Path to JSON file with projects data (default: test_projects.json)",
        )

    def handle(self, *args, **options):
        overwrite = options["force"]
        target_user = options["user"]
        wipe = options["clear"]
        json_path = options["file"]

        try:
            with open(json_path, encoding="utf-8") as f:
                catalogue = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл не найден: {json_path}"))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Ошибка разбора JSON: {e}"))
            return

        if wipe:
            self.wipe_projects(target_user)

        if target_user:
            catalogue = [p for p in catalogue if p["owner_username"] == target_user]
            if not catalogue:
                self.stdout.write(
                    self.style.WARNING(f"Нет проектов для пользователя {target_user}")
                )
                return

        self.populate_projects(catalogue, overwrite)

    def wipe_projects(self, target_user=None):
        if target_user:
            try:
                account = User.objects.get(username=target_user)
                removed = Project.objects.filter(owner=account).count()
                Project.objects.filter(owner=account).delete()
                self.stdout.write(
                    self.style.WARNING(
                        f"Удалено {removed} проектов пользователя {target_user}"
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Пользователь {target_user} не существует")
                )
        else:
            removed = Project.objects.all().count()
            Project.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Удалено {removed} проектов"))

    def populate_projects(self, catalogue, overwrite):
        created_num = 0
        updated_num = 0
        skipped_num = 0

        for spec in catalogue:
            title = spec["name"]
            login_name = spec["owner_username"]

            try:
                creator = User.objects.get(username=login_name)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'Пользователь {login_name} не существует. Пропускаем проект "{title}"'
                    )
                )
                skipped_num += 1
                continue

            already_exists = Project.objects.filter(name=title).exists()

            if already_exists and not overwrite:
                self.stdout.write(
                    self.style.WARNING(
                        f'Проект "{title}" уже существует. Используйте --force для перезаписи.'
                    )
                )
                skipped_num += 1
                continue

            if already_exists and overwrite:
                entry = Project.objects.get(name=title)
                entry.description = spec["description"]
                entry.github_url = spec.get("github_url", "")
                entry.status = spec["status"]
                entry.owner = creator
                entry.save()

                entry.participants.clear()
                for member_name in spec["participants_usernames"]:
                    try:
                        member = User.objects.get(username=member_name)
                        entry.participants.add(member)
                    except User.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Участник {member_name} не найден для проекта {title}"
                            )
                        )

                updated_num += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Обновлен проект: {title}"))
            else:
                entry = Project(
                    name=spec["name"],
                    description=spec["description"],
                    github_url=spec.get("github_url", ""),
                    status=spec["status"],
                    owner=creator,
                )
                entry.save()

                for member_name in spec["participants_usernames"]:
                    try:
                        member = User.objects.get(username=member_name)
                        entry.participants.add(member)
                    except User.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Участник {member_name} не найден для проекта {title}"
                            )
                        )

                created_num += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Создан проект: {title} (владелец: {login_name})"
                    )
                )

                if len(spec["participants_usernames"]) > 1:
                    crew = ", ".join(spec["participants_usernames"])
                    self.stdout.write(f"    Участники: {crew}")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("Статистика создания проектов:"))
        self.stdout.write(f"  Создано: {created_num}")
        self.stdout.write(f"  Обновлено: {updated_num}")
        self.stdout.write(f"  Пропущено: {skipped_num}")
        self.stdout.write("=" * 50)
