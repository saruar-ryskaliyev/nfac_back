from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.message import ApiResponse


class OptionBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    question_id: int
    option_text: str
    is_correct: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class OptionInCreate(BaseModel):
    option_text: str
    is_correct: bool = False


class OptionInUpdate(BaseModel):
    option_text: str | None = None
    is_correct: bool | None = None


class OptionOutData(OptionBase):
    pass


class OptionResponse(ApiResponse):
    message: str = "Option API Response"
    data: OptionOutData | list[OptionOutData]
    detail: dict[str, Any] | None = {"key": "val"}
