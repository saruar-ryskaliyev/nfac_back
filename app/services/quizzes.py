import logging

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.api.dependencies.database import get_repository
from app.core import constant
from app.database.repositories.quizzes import QuizzesRepository
from app.models.user import User
from app.schemas.quiz import (
    QuizInCreate,
    QuizInUpdate,
    QuizOutData,
    QuizResponse,
    QuizFilters,
)
from app.services.base import BaseService
from app.utils import ServiceResult, response_4xx, return_service

logger = logging.getLogger(__name__)


class QuizzesService(BaseService):
    @return_service
    async def create_quiz(
        self,
        creator: User,
        quiz_in: QuizInCreate,
        quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    ) -> ServiceResult:
        created_quiz = await quizzes_repo.create_quiz(creator=creator, quiz_in=quiz_in)

        return dict(
            status_code=HTTP_201_CREATED,
            content={
                "message": "Quiz created successfully.",
                "data": jsonable_encoder(QuizOutData.model_validate(created_quiz)),
            },
        )

    @return_service
    async def get_quiz_by_id(
        self,
        quiz_id: int,
        quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    ) -> ServiceResult:
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": "Quiz retrieved successfully.",
                "data": jsonable_encoder(QuizOutData.model_validate(quiz)),
            },
        )

    @return_service
    async def get_all_quizzes(
        self,
        quiz_filters: QuizFilters,
        quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    ) -> ServiceResult:
        quizzes = await quizzes_repo.get_public_quizzes(
            skip=quiz_filters.skip,
            limit=quiz_filters.limit
        )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": "Quizzes retrieved successfully.",
                "data": jsonable_encoder([QuizOutData.model_validate(quiz) for quiz in quizzes]),
            },
        )

    @return_service
    async def search_quizzes(
        self,
        quiz_filters: QuizFilters,
        quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    ) -> ServiceResult:
        if not quiz_filters.tag:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": "Tag parameter is required for search"},
            )

        quizzes = await quizzes_repo.search_quizzes_by_tag(
            tag=quiz_filters.tag,
            skip=quiz_filters.skip,
            limit=quiz_filters.limit
        )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": "Quizzes searched successfully.",
                "data": jsonable_encoder([QuizOutData.model_validate(quiz) for quiz in quizzes]),
            },
        )

    @return_service
    async def get_quizzes_by_user(
        self,
        user_id: int,
        quiz_filters: QuizFilters,
        quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    ) -> ServiceResult:
        quizzes = await quizzes_repo.get_quizzes_by_creator(
            creator_id=user_id,
            skip=quiz_filters.skip,
            limit=quiz_filters.limit
        )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": "User quizzes retrieved successfully.",
                "data": jsonable_encoder([QuizOutData.model_validate(quiz) for quiz in quizzes]),
            },
        )

    @return_service
    async def update_quiz(
        self,
        quiz_id: int,
        quiz_in: QuizInUpdate,
        quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    ) -> ServiceResult:
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        updated_quiz = await quizzes_repo.update_quiz(quiz=quiz, quiz_in=quiz_in)

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": "Quiz updated successfully.",
                "data": jsonable_encoder(QuizOutData.model_validate(updated_quiz)),
            },
        )

    @return_service
    async def delete_quiz(
        self,
        quiz_id: int,
        quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    ) -> ServiceResult:
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        await quizzes_repo.delete_quiz(quiz=quiz)

        return dict(
            status_code=HTTP_200_OK,
            content={"message": "Quiz deleted successfully."},
        )