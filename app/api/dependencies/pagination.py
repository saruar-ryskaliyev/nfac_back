from fastapi import Query

from app.schemas.pagination import PaginationParams


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    skip: int = Query(None, ge=0, description="Number of records to skip (overrides page)"),
) -> PaginationParams:
    # If skip is provided, use it directly, otherwise calculate from page
    if skip is not None:
        return PaginationParams(skip=skip, limit=limit)
    else:
        calculated_skip = (page - 1) * limit
        return PaginationParams(skip=calculated_skip, limit=limit)