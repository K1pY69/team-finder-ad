from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.constants import STATUS_CLOSED, STATUS_OPEN
from projects.forms import ProjectForm
from projects.models import Project
from projects.service import paginate
from users.models import Skill
from users.service import handle_skill_add


def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants")
    page = paginate(projects, request.GET.get("page"))
    return render(request, "projects/project_list.html", {"projects": page})


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return redirect("projects:detail", project_id=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def project_complete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"}, status=HTTPStatus.FORBIDDEN
        )
    if project.status != STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже закрыт"}, status=HTTPStatus.BAD_REQUEST
        )
    project.status = STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": STATUS_CLOSED})


@login_required
@require_POST
def project_toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    is_participant = project.participants.filter(pk=user.pk).exists()
    if is_participant:
        project.participants.remove(user)
        added = False
    else:
        if project.status != STATUS_OPEN:
            return JsonResponse(
                {"status": "error", "message": "Нельзя вступить в закрытый проект"},
                status=HTTPStatus.BAD_REQUEST,
            )
        project.participants.add(user)
        added = True
    return JsonResponse({"status": "ok", "participant": added})


@login_required
@require_POST
def skill_add(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"}, status=HTTPStatus.FORBIDDEN
        )
    return handle_skill_add(request.body, project)


@login_required
@require_POST
def skill_remove(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"}, status=HTTPStatus.FORBIDDEN
        )
    skill = get_object_or_404(Skill, pk=skill_id)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
