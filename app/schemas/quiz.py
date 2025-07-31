from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.message import ApiResponse


class QuizBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    title: str
    description: str | None = None
    creator_id: int
    is_public: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class QuizInCreate(BaseModel):
    title: str
    description: str | None = None
    is_public: bool = True


class QuizInUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_public: bool | None = None


class QuizFilters(BaseModel):
    skip: int | None = 0
    limit: int | None = 100
    tag: str | None = None


class QuizOutData(QuizBase):
    pass


class QuizResponse(ApiResponse):
    message: str = "Quiz API Response"
    data: QuizOutData | list[QuizOutData]
    detail: dict[str, Any] | None = {"key": "val"}