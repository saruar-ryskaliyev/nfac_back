from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.api.dependencies.auth import get_current_admin_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.quizzes import get_quiz_filters
from app.api.dependencies.service import get_service
from app.database.repositories.quizzes import QuizzesRepository
from app.models.user import User
from app.schemas.quiz import QuizFilters, QuizInCreate, QuizInUpdate, QuizResponse
from app.services.quizzes import QuizzesService
from app.utils import ERROR_RESPONSES

router = APIRouter()


@router.post(
    path="/",
    status_code=HTTP_201_CREATED,
    response_model=QuizResponse,
    responses=ERROR_RESPONSES,
    name="quizzes:create",
)
async def create_quiz(
    *,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    quiz_in: QuizInCreate,
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Create a new quiz.
    """
    result = await quizzes_service.create_quiz(
        creator=current_user,
        quiz_in=quiz_in,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.get(
    path="/",
    status_code=HTTP_200_OK,
    response_model=QuizResponse,
    responses=ERROR_RESPONSES,
    name="quizzes:get_all",
)
async def get_all_quizzes(
    *,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    quiz_filters: QuizFilters = Depends(get_quiz_filters),
):
    """
    Get all public quizzes.
    """
    result = await quizzes_service.get_all_quizzes(
        quiz_filters=quiz_filters,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.get(
    path="/{quiz_id}",
    status_code=HTTP_200_OK,
    response_model=QuizResponse,
    responses=ERROR_RESPONSES,
    name="quizzes:get_by_id",
)
async def get_quiz_by_id(
    *,
    quiz_id: int,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
):
    """
    Get a quiz by ID.
    """
    result = await quizzes_service.get_quiz_by_id(
        quiz_id=quiz_id,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.get(
    path="/search",
    status_code=HTTP_200_OK,
    response_model=QuizResponse,
    responses=ERROR_RESPONSES,
    name="quizzes:search",
)
async def search_quizzes(
    *,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    quiz_filters: QuizFilters = Depends(get_quiz_filters),
):
    """
    Search quizzes by tag.
    """
    result = await quizzes_service.search_quizzes(
        quiz_filters=quiz_filters,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.get(
    path="/user/{user_id}",
    status_code=HTTP_200_OK,
    response_model=QuizResponse,
    responses=ERROR_RESPONSES,
    name="quizzes:get_by_user",
)
async def get_quizzes_by_user(
    *,
    user_id: int,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    quiz_filters: QuizFilters = Depends(get_quiz_filters),
):
    """
    Get quizzes created by a specific user.
    """
    result = await quizzes_service.get_quizzes_by_user(
        user_id=user_id,
        quiz_filters=quiz_filters,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.put(
    path="/{quiz_id}",
    status_code=HTTP_200_OK,
    response_model=QuizResponse,
    responses=ERROR_RESPONSES,
    name="quizzes:update",
)
async def update_quiz(
    *,
    quiz_id: int,
    quiz_in: QuizInUpdate,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Update a quiz by ID (admin only).
    """
    result = await quizzes_service.update_quiz(
        quiz_id=quiz_id,
        quiz_in=quiz_in,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.delete(
    path="/{quiz_id}",
    status_code=HTTP_200_OK,
    name="quizzes:delete",
)
async def delete_quiz(
    *,
    quiz_id: int,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Delete a quiz by ID (admin only).
    """
    result = await quizzes_service.delete_quiz(
        quiz_id=quiz_id,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()
