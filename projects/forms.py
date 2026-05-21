from django import forms

from projects.models import Project
from team_finder.mixins import GithubUrlMixin


class ProjectForm(GithubUrlMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
