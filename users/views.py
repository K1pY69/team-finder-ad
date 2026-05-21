from http import HTTPStatus

from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from team_finder.service import paginate
from users.constants import AUTOCOMPLETE_LIMIT, USERS_PER_PAGE
from users.forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from users.models import Skill
from users.service import handle_skill_add

User = get_user_model()


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        User.objects.create_user(
            email=data["email"],
            name=data["name"],
            surname=data["surname"],
            password=data["password"],
        )
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None, request=request)
    if form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_list(request):
    active_skill = request.GET.get("skill", "").strip() or None
    users = User.objects.order_by("id")
    if active_skill:
        users = users.filter(skills__name=active_skill)
    all_skills = Skill.objects.all()
    page = paginate(users, request.GET.get("page"), USERS_PER_PAGE)
    return render(
        request,
        "users/participants.html",
        {"participants": page, "all_skills": all_skills, "active_skill": active_skill},
    )


def user_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return redirect("users:edit_profile", user_id=request.user.id)
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        user = form.save()
        return redirect("users:detail", user_id=user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return redirect("users:change_password", user_id=request.user.id)
    form = ChangePasswordForm(request.POST or None, user=request.user)
    if form.is_valid():
        request.user.set_password(form.cleaned_data["new_password1"])
        request.user.save()
        update_session_auth_hash(request, request.user)
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/change_password.html", {"form": form})


def skills_autocomplete(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__icontains=query).order_by("name")[:AUTOCOMPLETE_LIMIT]
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required
@require_POST
def add_user_skill(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
    return handle_skill_add(request.body, profile_user)


@login_required
@require_POST
def remove_user_skill(request, user_id, skill_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
    skill = get_object_or_404(Skill, pk=skill_id)
    profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
