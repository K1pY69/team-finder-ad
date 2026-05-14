from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("list/", views.user_list, name="list"),
    path("<int:user_id>/", views.user_detail, name="detail"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("<int:user_id>/edit/", views.edit_profile, name="edit_profile"),
    path("<int:user_id>/change-password/", views.change_password, name="change_password"),
    path("skills/", views.skills_autocomplete, name="skills_autocomplete"),
    path("<int:user_id>/skills/add/", views.add_user_skill, name="add_skill"),
    path(
        "<int:user_id>/skills/<int:skill_id>/remove/",
        views.remove_user_skill,
        name="remove_skill",
    ),
]
