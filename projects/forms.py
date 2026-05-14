from urllib.parse import urlparse

from django import forms

from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "status": forms.Select(choices=[("open", "Открыт"), ("closed", "Закрыт")]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["github_url"].required = False
        self.fields["status"].required = True

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if not url:
            return url
        parsed = urlparse(url)
        if not parsed.scheme or "github.com" not in parsed.netloc:
            raise forms.ValidationError("Ссылка должна вести на GitHub (github.com)")
        return url
