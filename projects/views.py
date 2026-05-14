import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from users.models import Skill

from projects.forms import ProjectForm
from projects.models import Project


def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants").order_by(
        "-created_at"
    )
    paginator = Paginator(projects, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "projects/project_list.html", {"projects": page})


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f"/projects/{project.pk}/")
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return redirect(f"/projects/{project.pk}/")
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f"/projects/{project.pk}/")
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def project_complete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return JsonResponse({"status": "error", "message": "Нет прав"}, status=403)
    if project.status != "open":
        return JsonResponse({"status": "error", "message": "Проект уже закрыт"}, status=400)
    project.status = "closed"
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
@require_POST
def project_toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    is_participant = project.participants.filter(pk=user.pk).exists()
    if is_participant:
        project.participants.remove(user)
        added = False
    else:
        if project.status != "open":
            return JsonResponse(
                {"status": "error", "message": "Нельзя вступить в закрытый проект"},
                status=400,
            )
        project.participants.add(user)
        added = True
    return JsonResponse({"status": "ok", "participant": added})


@login_required
@require_POST
def skill_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return JsonResponse({"status": "error", "message": "Нет прав"}, status=403)
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

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse({
        "skill_id": skill.pk,
        "name": skill.name,
        "created": created,
        "added": added,
    })


@login_required
@require_POST
def skill_remove(request, pk, skill_pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return JsonResponse({"status": "error", "message": "Нет прав"}, status=403)
    skill = get_object_or_404(Skill, pk=skill_pk)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})


def skills_autocomplete(request):
    q = request.GET.get("q", "").strip()
    qs = Skill.objects.filter(name__icontains=q).order_by("name")[:10]
    return JsonResponse(list(qs.values("id", "name")), safe=False)
