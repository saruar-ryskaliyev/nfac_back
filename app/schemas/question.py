from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.message import ApiResponse
from app.schemas.option import OptionInCreate, OptionOutData


class QuestionBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    quiz_id: int
    question_text: str
    question_type: Literal["single", "multiple", "text"]
    points: int = 1
    options: list[OptionOutData] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class QuestionInCreate(BaseModel):
    quiz_id: int
    question_text: str
    question_type: Literal["single", "multiple", "text"]
    points: int = 1
    options: list[OptionInCreate] = []


class QuestionInUpdate(BaseModel):
    question_text: str | None = None
    question_type: Literal["single", "multiple", "text"] | None = None
    points: int | None = None
    options: list[OptionInCreate] | None = None


class QuestionFilters(BaseModel):
    skip: int | None = 0
    limit: int | None = 100


class QuestionOutData(QuestionBase):
    pass


class QuestionResponse(ApiResponse):
    message: str = "Question API Response"
    data: QuestionOutData | list[QuestionOutData] | None = None
    detail: dict[str, Any] | None = {"key": "val"}
