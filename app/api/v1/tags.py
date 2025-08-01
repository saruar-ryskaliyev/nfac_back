from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.api.dependencies.auth import get_current_admin_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.service import get_service
from app.database.repositories.tags import TagsRepository
from app.models.user import User
from app.schemas.tag import TagFilters, TagInCreate, TagInUpdate, TagResponse
from app.services.tags import TagsService
from app.utils import ERROR_RESPONSES

router = APIRouter()


@router.post(
    path="/",
    status_code=HTTP_201_CREATED,
    response_model=TagResponse,
    responses=ERROR_RESPONSES,
    name="tags:create",
)
async def create_tag(
    *,
    tags_service: TagsService = Depends(get_service(TagsService)),
    tags_repo: TagsRepository = Depends(get_repository(TagsRepository)),
    tag_in: TagInCreate,
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Create a new tag (admin only).
    """
    result = await tags_service.create_tag(
        tag_in=tag_in,
        tags_repo=tags_repo,
    )

    return await result.unwrap()


@router.get(
    path="/",
    status_code=HTTP_200_OK,
    response_model=TagResponse,
    responses=ERROR_RESPONSES,
    name="tags:get_all",
)
async def get_all_tags(
    *,
    tags_service: TagsService = Depends(get_service(TagsService)),
    tags_repo: TagsRepository = Depends(get_repository(TagsRepository)),
    tag_filters: TagFilters = Depends(),
):
    """
    Get all tags.
    """
    result = await tags_service.get_all_tags(
        tag_filters=tag_filters,
        tags_repo=tags_repo,
    )

    return await result.unwrap()


@router.get(
    path="/{tag_id}",
    status_code=HTTP_200_OK,
    response_model=TagResponse,
    responses=ERROR_RESPONSES,
    name="tags:get_by_id",
)
async def get_tag_by_id(
    *,
    tag_id: int,
    tags_service: TagsService = Depends(get_service(TagsService)),
    tags_repo: TagsRepository = Depends(get_repository(TagsRepository)),
):
    """
    Get a tag by ID.
    """
    result = await tags_service.get_tag_by_id(
        tag_id=tag_id,
        tags_repo=tags_repo,
    )

    return await result.unwrap()


@router.put(
    path="/{tag_id}",
    status_code=HTTP_200_OK,
    response_model=TagResponse,
    responses=ERROR_RESPONSES,
    name="tags:update",
)
async def update_tag(
    *,
    tag_id: int,
    tag_in: TagInUpdate,
    tags_service: TagsService = Depends(get_service(TagsService)),
    tags_repo: TagsRepository = Depends(get_repository(TagsRepository)),
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Update a tag by ID (admin only).
    """
    result = await tags_service.update_tag(
        tag_id=tag_id,
        tag_in=tag_in,
        tags_repo=tags_repo,
    )

    return await result.unwrap()


@router.delete(
    path="/{tag_id}",
    status_code=HTTP_200_OK,
    name="tags:delete",
)
async def delete_tag(
    *,
    tag_id: int,
    tags_service: TagsService = Depends(get_service(TagsService)),
    tags_repo: TagsRepository = Depends(get_repository(TagsRepository)),
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Delete a tag by ID (admin only).
    """
    result = await tags_service.delete_tag(
        tag_id=tag_id,
        tags_repo=tags_repo,
    )

    return await result.unwrap()