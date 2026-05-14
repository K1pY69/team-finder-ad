from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.models import UserProfile

TEST_USER_ROSTER = [
    {
        "username": "kirill_morozov",
        "first_name": "Кирилл",
        "last_name": "Морозов",
        "email": "kirill.morozov92@gmail.com",
        "password": "K7_moroz!spring",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "avatar": "avatars/kirill_morozov_avatar.jpg",
            "about": (
                "Python-разработчик, люблю Django и чистые API. "
                "В выходные гоняю на велосипеде по набережной."
            ),
            "phone": "+7 (916) 204-88-31",
            "github_url": "https://github.com/kirill-morozov-demo",
        },
    },
    {
        "username": "svetlana_kozlova",
        "first_name": "Светлана",
        "last_name": "Козлова",
        "email": "svetlana.kozlova.work@yandex.ru",
        "password": "TeaRabbit#44",
        "is_staff": True,
        "is_superuser": False,
        "profile": {
            "avatar": "avatars/svetlana_kozlova_avatar.jpg",
            "about": (
                "Team lead и full-stack: от схемы БД до релиза. "
                "Пью зелёный чай и веду заметки в Obsidian."
            ),
            "phone": "+7 (903) 771-42-09",
            "github_url": "https://github.com/svetlana-kozlova-demo",
        },
    },
    {
        "username": "nikita_orlov",
        "first_name": "Никита",
        "last_name": "Орлов",
        "email": "nikita.orlov.dev@mail.ru",
        "password": "RiverDjango_19",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "avatar": "",
            "about": (
                "Начинающий разработчик: осваиваю Django и тесты. "
                "Ищу первый коммерческий проект и открыт к парному программированию."
            ),
            "phone": None,
            "github_url": "https://github.com/nikita-orlov-demo",
        },
    },
    {
        "username": "olga_petrova",
        "first_name": "Ольга",
        "last_name": "Петрова",
        "email": "olga.petrova.tech@gmail.com",
        "password": "PixelGarden8*",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "avatar": "avatars/olga_petrova_avatar.jpg",
            "about": (
                "Frontend: React и доступность интерфейсов. "
                "Вечером рисую интерфейсы в Figma «для души»."
            ),
            "phone": "+7 (981) 556-12-74",
            "github_url": "https://github.com/olga-petrova-demo",
        },
    },
    {
        "username": "team_admin",
        "first_name": "Илья",
        "last_name": "Сергеев",
        "email": "maintainer.platform@tools.dev",
        "password": "SysVault_404secure",
        "is_staff": True,
        "is_superuser": True,
        "profile": {
            "avatar": "",
            "about": (
                "Платформенный администратор: CI, бэкапы и мониторинг. "
                "Пишу runbook'и, чтобы ночью никто не звонил."
            ),
            "phone": "+7 (495) 228-90-01",
            "github_url": "https://github.com/team-admin-demo",
        },
    },
]


class Command(BaseCommand):
    help = "Create test users with their profiles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreate users even if they exist",
        )
        parser.add_argument(
            "--only-profile",
            action="store_true",
            help="Create only user profiles for existing users",
        )

    def handle(self, *args, **options):
        overwrite = options["force"]
        profiles_only = options["only_profile"]

        if profiles_only:
            self.build_profiles(TEST_USER_ROSTER, overwrite)
        else:
            self.build_accounts(TEST_USER_ROSTER, overwrite)

    def build_accounts(self, roster, overwrite):
        for spec in roster:
            login_name = spec["username"]

            already_exists = User.objects.filter(username=login_name).exists()

            if already_exists and not overwrite:
                self.stdout.write(
                    self.style.WARNING(
                        f"Пользователь {login_name} уже существует. "
                        f"Используйте --force для перезаписи."
                    )
                )
                continue

            if already_exists and overwrite:
                User.objects.filter(username=login_name).delete()
                self.stdout.write(f"Удален существующий пользователь {login_name}")

            account = User.objects.create_user(
                username=spec["username"],
                email=spec["email"],
                password=spec["password"],
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                is_staff=spec["is_staff"],
                is_superuser=spec["is_superuser"],
            )

            pd = spec["profile"]
            bio_entry = UserProfile(
                user=account,
                avatar=pd["avatar"] if pd["avatar"] else None,
                about=pd["about"],
                phone=pd["phone"],
                github_url=pd["github_url"],
            )
            bio_entry.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Создан пользователь: {login_name} (пароль: {spec['password']})"
                )
            )

    def build_profiles(self, roster, overwrite):
        for spec in roster:
            login_name = spec["username"]

            try:
                account = User.objects.get(username=login_name)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Пользователь {login_name} не существует. "
                        f"Сначала создайте пользователя."
                    )
                )
                continue

            has_profile = UserProfile.objects.filter(user=account).exists()

            if has_profile and not overwrite:
                self.stdout.write(
                    self.style.WARNING(
                        f"Профиль для {login_name} уже существует. "
                        f"Используйте --force для обновления."
                    )
                )
                continue

            if has_profile and overwrite:
                UserProfile.objects.filter(user=account).delete()
                self.stdout.write(f"Удален существующий профиль для {login_name}")

            pd = spec["profile"]
            bio_entry = UserProfile(
                user=account,
                avatar=pd["avatar"] if pd["avatar"] else None,
                about=pd["about"],
                phone=pd["phone"],
                github_url=pd["github_url"],
            )
            bio_entry.save()

            self.stdout.write(self.style.SUCCESS(f"✓ Создан профиль для: {login_name}"))
