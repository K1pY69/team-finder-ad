import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate

from users.models import User


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=124, label="Имя")
    surname = forms.CharField(max_length=124, label="Фамилия")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


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


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "email", "avatar", "about", "phone", "github_url"]
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Имя"
        self.fields["surname"].label = "Фамилия"
        self.fields["email"].label = "Email"
        self.fields["email"].required = True
        self.fields["avatar"].label = "Фото профиля"
        self.fields["avatar"].required = False
        self.fields["about"].label = "О себе"
        self.fields["phone"].label = "Телефон"
        self.fields["phone"].required = False
        self.fields["github_url"].label = "GitHub"
        self.fields["github_url"].required = False

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

    def clean_github_url(self):
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return url
        parsed = urlparse(url)
        if not parsed.scheme or "github.com" not in parsed.netloc:
            raise forms.ValidationError("Ссылка должна вести на GitHub (github.com)")
        return url


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
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Новые пароли не совпадают")
        return cleaned
