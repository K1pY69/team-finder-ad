from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from users.constants import (
    ABOUT_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
)
from users.managers import UserManager
from users.utils import generate_avatar


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, verbose_name="Название")

    class Meta:
        ordering = ["name"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name="Имя")
    surname = models.CharField(max_length=SURNAME_MAX_LENGTH, verbose_name="Фамилия")
    avatar = models.ImageField(upload_to="avatars/", blank=True, verbose_name="Аватар")
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Телефон",
    )
    github_url = models.URLField(blank=True, verbose_name="Ссылка на GitHub")
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True, verbose_name="О себе")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Сотрудник")
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="users",
        verbose_name="Навыки",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.avatar:
            avatar_file = generate_avatar(self.name)
            self.avatar.save(avatar_file.name, avatar_file, save=False)
        super().save(*args, **kwargs)
