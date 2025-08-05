from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 20


class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
    has_next: bool
    has_previous: bool
    total_pages: int
    current_page: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta