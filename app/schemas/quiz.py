from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.message import ApiResponse
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.schemas.tag import TagOutData
from app.schemas.question import QuestionOutData, QuestionInQuizCreate


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
    questions: list[QuestionInQuizCreate] = []


class QuizInUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_public: bool | None = None
    tag_names: list[str] | None = None
    questions: list[QuestionInQuizCreate] | None = None


class QuizGenerateRequest(BaseModel):
    prompt: str
    num_questions: int = 5
    is_public: bool = True
    tag_names: list[str] = []


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


class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    username: str
    score: int
    attempt_number: int
    finished_at: datetime | None = None


class LeaderboardData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    quiz_id: int
    quiz_title: str
    entries: list[LeaderboardEntry] = []


class LeaderboardResponse(ApiResponse):
    message: str = "Quiz Leaderboard Response"
    data: LeaderboardData | None = None
    detail: dict[str, Any] | None = None


class QuizPaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    message: str = "Quiz API Response"
    data: PaginatedResponse[QuizOutData] | dict[str, Any] | None = None
    detail: dict[str, Any] | None = None
