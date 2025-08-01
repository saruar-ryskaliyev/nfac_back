from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.message import ApiResponse


class TagBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class TagInCreate(BaseModel):
    name: str


class TagInUpdate(BaseModel):
    name: str | None = None


class TagFilters(BaseModel):
    skip: int | None = 0
    limit: int | None = 100


class TagOutData(TagBase):
    pass


class TagResponse(ApiResponse):
    message: str = "Tag API Response"
    data: TagOutData | list[TagOutData] | None = None
    detail: dict[str, Any] | None = {"key": "val"}