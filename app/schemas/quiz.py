from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.message import ApiResponse
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.schemas.tag import TagOutData
from app.schemas.question import QuestionOutData


class QuizBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    title: str
    description: str | None = None
    creator_id: int
    is_public: bool = True
    tags: list[TagOutData] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class QuizInCreate(BaseModel):
    title: str
    description: str | None = None
    is_public: bool = True
    tag_names: list[str]


class QuizInUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_public: bool | None = None
    tag_names: list[str] | None = None


class QuizFilters(PaginationParams):
    tag: str | None = None
    search: str | None = None


class QuizOutData(QuizBase):
    pass


class QuizDetailData(QuizBase):
    questions: list[QuestionOutData] = []


class QuizResponse(ApiResponse):
    message: str = "Quiz API Response"
    data: QuizOutData | list[QuizOutData] | dict[str, Any] | None = None
    detail: dict[str, Any] | None = {"key": "val"}


class QuizDetailResponse(ApiResponse):
    message: str = "Quiz API Response"
    data: QuizDetailData | None = None
    detail: dict[str, Any] | None = {"key": "val"}


class QuizPaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    message: str = "Quiz API Response"
    data: PaginatedResponse[QuizOutData] | dict[str, Any] | None = None
    detail: dict[str, Any] | None = None
