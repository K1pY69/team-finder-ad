from projects.constants import PROJECTS_PER_PAGE
from team_finder.service import paginate as _paginate


def paginate(queryset, page_number):
    return _paginate(queryset, page_number, PROJECTS_PER_PAGE)
