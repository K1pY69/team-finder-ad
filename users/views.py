import json

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from users.forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from users.models import Skill, User


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            User.objects.create_user(
                email=d["email"],
                name=d["name"],
                surname=d["surname"],
                password=d["password"],
            )
            return redirect("/users/login/")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("/projects/list/")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


def user_list(request):
    active_skill = request.GET.get("skill", "").strip() or None
    users = User.objects.order_by("id")
    if active_skill:
        users = users.filter(skills__name=active_skill)
    all_skills = Skill.objects.all()
    paginator = Paginator(users, 12)
    page = paginator.get_page(request.GET.get("page"))
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
        return redirect(f"/users/{request.user.id}/edit/")
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            return redirect(f"/users/{user.id}/")
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return redirect(f"/users/{request.user.id}/change-password/")
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password1"])
            request.user.save()
            update_session_auth_hash(request, request.user)
            return redirect(f"/users/{request.user.id}/")
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, "users/change_password.html", {"form": form})


def skills_autocomplete(request):
    q = request.GET.get("q", "").strip()
    qs = Skill.objects.filter(name__icontains=q).order_by("name")[:10]
    return JsonResponse(list(qs.values("id", "name")), safe=False)


@login_required
@require_POST
def add_user_skill(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Bad JSON"}, status=400)

    skill_id = data.get("skill_id")
    name = data.get("name", "").strip()

    created = False
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "skill_id or name required"}, status=400)

    added = not profile_user.skills.filter(pk=skill.pk).exists()
    if added:
        profile_user.skills.add(skill)

    return JsonResponse(
        {"skill_id": skill.id, "name": skill.name, "created": created, "added": added}
    )


@login_required
@require_POST
def remove_user_skill(request, user_id, skill_id):
    profile_user = get_object_or_404(User, pk=user_id)
    if profile_user.pk != request.user.pk:
        return JsonResponse({"error": "Forbidden"}, status=403)
    skill = get_object_or_404(Skill, pk=skill_id)
    profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
