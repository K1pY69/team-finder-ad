from django.urls import path

from projects import views
from users.views import skills_autocomplete

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list, name="list"),
    path("create-project/", views.project_create, name="create"),
    path("skills/", skills_autocomplete, name="skills_autocomplete"),
    path("<int:project_id>/", views.project_detail, name="detail"),
    path("<int:project_id>/edit/", views.project_edit, name="edit"),
    path("<int:project_id>/complete/", views.project_complete, name="complete"),
    path(
        "<int:project_id>/toggle-participate/",
        views.project_toggle_participate,
        name="toggle_participate",
    ),
    path("<int:project_id>/skills/add/", views.skill_add, name="skill_add"),
    path(
        "<int:project_id>/skills/<int:skill_id>/remove/",
        views.skill_remove,
        name="skill_remove",
    ),
]
