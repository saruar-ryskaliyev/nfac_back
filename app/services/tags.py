import logging

from starlette.status import (
    HTTP_404_NOT_FOUND,
)

from app.database.repositories.tags import TagsRepository
from app.schemas.tag import (
    TagFilters,
    TagInCreate,
    TagInUpdate,
    TagOutData,
    TagResponse,
)
from app.services.base import BaseService
from app.utils import response_4xx, return_service

logger = logging.getLogger(__name__)


class TagsService(BaseService):
    @return_service
    async def create_tag(
        self,
        tag_in: TagInCreate,
        tags_repo: TagsRepository,
    ):
        created_tag = await tags_repo.create_tag(tag_in=tag_in)

        return TagResponse(
            message="Tag created successfully.",
            data=TagOutData.model_validate(created_tag),
        )

    @return_service
    async def get_tag_by_id(
        self,
        tag_id: int,
        tags_repo: TagsRepository,
    ):
        tag = await tags_repo.get_tag_by_id(tag_id=tag_id)
        if not tag:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Tag not found"},
            )

        return TagResponse(
            message="Tag retrieved successfully.",
            data=TagOutData.model_validate(tag),
        )

    @return_service
    async def get_all_tags(
        self,
        tag_filters: TagFilters,
        tags_repo: TagsRepository,
    ):
        tags = await tags_repo.get_all_tags(skip=tag_filters.skip, limit=tag_filters.limit)

        return TagResponse(
            message="Tags retrieved successfully.",
            data=[TagOutData.model_validate(tag) for tag in tags],
        )

    @return_service
    async def update_tag(
        self,
        tag_id: int,
        tag_in: TagInUpdate,
        tags_repo: TagsRepository,
    ):
        tag = await tags_repo.get_tag_by_id(tag_id=tag_id)
        if not tag:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Tag not found"},
            )

        updated_tag = await tags_repo.update_tag(tag=tag, tag_in=tag_in)

        return TagResponse(
            message="Tag updated successfully.",
            data=TagOutData.model_validate(updated_tag),
        )

    @return_service
    async def delete_tag(
        self,
        tag_id: int,
        tags_repo: TagsRepository,
    ):
        tag = await tags_repo.get_tag_by_id(tag_id=tag_id)
        if not tag:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Tag not found"},
            )

        await tags_repo.delete_tag(tag=tag)

        return TagResponse(
            message="Tag deleted successfully.",
            data=None,
        )