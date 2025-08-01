from fastapi import Query

from app.schemas.quiz import QuizFilters


def get_quiz_filters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    tag: str = Query(None),
) -> QuizFilters:
    return QuizFilters(skip=skip, limit=limit, tag=tag)
