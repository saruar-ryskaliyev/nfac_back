from fastapi import Query, Depends

from app.schemas.quiz import QuizFilters
from app.schemas.pagination import PaginationParams
from app.api.dependencies.pagination import get_pagination_params


def get_quiz_filters(
    pagination: PaginationParams = Depends(get_pagination_params),
    tag: str = Query(None, description="Filter by tag name"),
    search: str = Query(None, description="Search text in quiz titles and descriptions"),
) -> QuizFilters:
    return QuizFilters(skip=pagination.skip, limit=pagination.limit, tag=tag, search=search)
