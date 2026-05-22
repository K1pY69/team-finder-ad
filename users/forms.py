import re

from django import forms
from django.contrib.auth import authenticate, get_user_model

from team_finder.mixins import GithubUrlMixin
from users.constants import NAME_MAX_LENGTH

User = get_user_model()


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=NAME_MAX_LENGTH, label="Имя")
    surname = forms.CharField(max_length=NAME_MAX_LENGTH, label="Фамилия")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован")
        return email


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный имейл или пароль")
            cleaned["user"] = user
        return cleaned


class EditProfileForm(GithubUrlMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "email", "avatar", "about", "phone", "github_url"]
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return phone
        pattern = re.compile(r"^(\+7|8)\d{10}$")
        if not pattern.match(phone):
            raise forms.ValidationError(
                "Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )
        if phone.startswith("8"):
            phone = "+7" + phone[1:]
        qs = User.objects.filter(phone=phone)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Такой номер телефона уже зарегистрирован")
        return phone


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Старый пароль")
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Повторите новый пароль")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old = self.cleaned_data.get("old_password")
        if not self.user.check_password(old):
            raise forms.ValidationError("Старый пароль введён неверно")
        return old

    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get("new_password1")
        confirm_password = cleaned.get("new_password2")
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Новые пароли не совпадают")
        return cleaned
