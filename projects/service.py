from projects.constants import PROJECTS_PER_PAGE
from team_finder.service import paginate as _paginate


def paginate(queryset, request, per_page=PROJECTS_PER_PAGE):
    return _paginate(queryset, request.GET.get("page"), per_page)
