from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list, name="list"),
    path("create-project/", views.project_create, name="create"),
    path("skills/", views.skills_autocomplete, name="skills_autocomplete"),
    path("<int:pk>/", views.project_detail, name="detail"),
    path("<int:pk>/edit/", views.project_edit, name="edit"),
    path("<int:pk>/complete/", views.project_complete, name="complete"),
    path(
        "<int:pk>/toggle-participate/",
        views.project_toggle_participate,
        name="toggle_participate",
    ),
    path("<int:pk>/skills/add/", views.skill_add, name="skill_add"),
    path(
        "<int:pk>/skills/<int:skill_pk>/remove/",
        views.skill_remove,
        name="skill_remove",
    ),
]
