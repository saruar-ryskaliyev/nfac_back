import logging

from starlette.status import (
    HTTP_404_NOT_FOUND,
)

from app.database.repositories.quizzes import QuizzesRepository
from app.database.repositories.tags import TagsRepository
from app.database.repositories.questions import QuestionsRepository
from app.database.repositories.options import OptionsRepository
from app.schemas.question import QuestionInCreate
from app.models.user import User
from app.schemas.quiz import (
    QuizFilters,
    QuizInCreate,
    QuizInUpdate,
    QuizOutData,
    QuizDetailData,
    QuizResponse,
    QuizDetailResponse,
    QuizPaginatedResponse,
)
from app.services.base import BaseService
from app.utils import response_4xx, return_service

logger = logging.getLogger(__name__)


class QuizzesService(BaseService):
    @return_service
    async def create_quiz(
        self,
        creator: User,
        quiz_in: QuizInCreate,
        quizzes_repo: QuizzesRepository,
        tags_repo: TagsRepository,
        questions_repo: QuestionsRepository | None = None,
        options_repo: OptionsRepository | None = None,
    ):
        tags = await tags_repo.get_or_create_tags(tag_names=quiz_in.tag_names)
        created_quiz = await quizzes_repo.create_quiz(creator=creator, quiz_in=quiz_in, tags=tags)

        if quiz_in.questions and questions_repo and options_repo:
            for question_data in quiz_in.questions:
                question_in_create = QuestionInCreate(
                    quiz_id=created_quiz.id,
                    question_text=question_data.question_text,
                    question_type=question_data.question_type,
                    points=question_data.points,
                    options=question_data.options
                )
                created_question = await questions_repo.create_question(question_in=question_in_create)
                
                if question_data.options:
                    await options_repo.create_options_for_question(
                        options_in=question_data.options, 
                        question_id=created_question.id
                    )
            
            await quizzes_repo.connection.commit()
            created_quiz = await quizzes_repo.get_quiz_by_id(quiz_id=created_quiz.id)

        return QuizResponse(
            message="Quiz created successfully.",
            data=QuizOutData.model_validate(created_quiz),
        )

    @return_service
    async def get_quiz_by_id(
        self,
        quiz_id: int,
        quizzes_repo: QuizzesRepository,
    ):
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        return QuizDetailResponse(
            message="Quiz retrieved successfully.",
            data=QuizDetailData.model_validate(quiz),
        )

    @return_service
    async def get_all_quizzes(
        self,
        quiz_filters: QuizFilters,
        quizzes_repo: QuizzesRepository,
    ):
        quizzes, meta = await quizzes_repo.get_public_quizzes_paginated(skip=quiz_filters.skip, limit=quiz_filters.limit)

        return QuizResponse(
            message="Quizzes retrieved successfully.",
            data={
                "data": [QuizOutData.model_validate(quiz) for quiz in quizzes],
                "meta": meta.model_dump()
            },
        )

    @return_service
    async def search_quizzes(
        self,
        quiz_filters: QuizFilters,
        quizzes_repo: QuizzesRepository,
    ):
        if quiz_filters.search:
            quizzes, meta = await quizzes_repo.search_quizzes_by_text_paginated(search_text=quiz_filters.search, skip=quiz_filters.skip, limit=quiz_filters.limit)
            message = f"Quizzes searched successfully for '{quiz_filters.search}'."
        elif quiz_filters.tag:
            quizzes, meta = await quizzes_repo.search_quizzes_by_tag_paginated(tag=quiz_filters.tag, skip=quiz_filters.skip, limit=quiz_filters.limit)
            message = f"Quizzes searched successfully for tag '{quiz_filters.tag}'."
        else:
            quizzes, meta = await quizzes_repo.get_all_quizzes_paginated(skip=quiz_filters.skip, limit=quiz_filters.limit)
            message = "All public quizzes retrieved successfully."

        return QuizPaginatedResponse(
            message=message,
            data={
                "data": [QuizOutData.model_validate(quiz) for quiz in quizzes],
                "meta": meta.model_dump()
            },
        )

    @return_service
    async def get_quizzes_by_user(
        self,
        user_id: int,
        quiz_filters: QuizFilters,
        quizzes_repo: QuizzesRepository,
    ):
        quizzes, meta = await quizzes_repo.get_quizzes_by_creator_paginated(creator_id=user_id, skip=quiz_filters.skip, limit=quiz_filters.limit)

        return QuizPaginatedResponse(
            message="User quizzes retrieved successfully.",
            data={
                "data": [QuizOutData.model_validate(quiz) for quiz in quizzes],
                "meta": meta.model_dump()
            },
        )

    @return_service
    async def update_quiz(
        self,
        quiz_id: int,
        quiz_in: QuizInUpdate,
        quizzes_repo: QuizzesRepository,
        tags_repo: TagsRepository,
    ):
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        tags = None
        if quiz_in.tag_names is not None:
            tags = await tags_repo.get_or_create_tags(tag_names=quiz_in.tag_names)

        updated_quiz = await quizzes_repo.update_quiz(quiz=quiz, quiz_in=quiz_in, tags=tags)

        return QuizResponse(
            message="Quiz updated successfully.",
            data=QuizOutData.model_validate(updated_quiz),
        )

    @return_service
    async def delete_quiz(
        self,
        quiz_id: int,
        quizzes_repo: QuizzesRepository,
    ):
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        await quizzes_repo.delete_quiz(quiz=quiz)

        return QuizResponse(
            message="Quiz deleted successfully.",
            data=None,
        )
