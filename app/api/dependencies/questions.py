from fastapi import Query

from app.schemas.question import QuestionFilters


def get_question_filters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> QuestionFilters:
    return QuestionFilters(skip=skip, limit=limit)
