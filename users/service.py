import json
from http import HTTPStatus

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from users.models import Skill


def handle_skill_add(request_body, target):
    try:
        data = json.loads(request_body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Bad JSON"}, status=HTTPStatus.BAD_REQUEST)

    skill_id = data.get("skill_id")
    name = data.get("name", "").strip()

    created = False
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "skill_id or name required"}, status=HTTPStatus.BAD_REQUEST)

    added = not target.skills.filter(pk=skill.pk).exists()
    if added:
        target.skills.add(skill)

    return JsonResponse({
        "skill_id": skill.pk,
        "name": skill.name,
        "created": created,
        "added": added,
    })
