from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.message import ApiResponse


class AnswerBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    user_id: int
    question_id: int
    selected_option_ids: list[int] | None = None
    text_answer: str | None = None
    is_correct: bool | None = None
    submitted_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class AnswerSubmit(BaseModel):
    question_id: int
    selected_option_ids: list[int] | None = None
    text_answer: str | None = None


class AnswerInCreate(BaseModel):
    user_id: int
    question_id: int
    selected_option_ids: list[int] | None = None
    text_answer: str | None = None
    is_correct: bool | None = None


class AnswerFilters(BaseModel):
    skip: int | None = 0
    limit: int | None = 100
    user_id: int | None = None
    quiz_id: int | None = None


class AnswerOutData(AnswerBase):
    pass


class QuizResult(BaseModel):
    quiz_id: int
    user_id: int
    total_questions: int
    correct_answers: int
    total_points: int
    score_percentage: float
    answers: list[AnswerOutData]


class AnswerResponse(ApiResponse):
    message: str = "Answer API Response"
    data: AnswerOutData | list[AnswerOutData] | None = None
    detail: dict[str, Any] | None = {"key": "val"}


class QuizResultResponse(ApiResponse):
    message: str = "Quiz Result Response"
    data: QuizResult
    detail: dict[str, Any] | None = {"key": "val"}
