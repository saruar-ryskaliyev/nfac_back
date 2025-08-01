import logging

from starlette.status import (
    HTTP_404_NOT_FOUND,
)

from app.database.repositories.options import OptionsRepository
from app.database.repositories.questions import QuestionsRepository
from app.database.repositories.quizzes import QuizzesRepository
from app.schemas.question import (
    QuestionFilters,
    QuestionInCreate,
    QuestionInUpdate,
    QuestionOutData,
    QuestionResponse,
)
from app.services.base import BaseService
from app.utils import response_4xx, return_service

logger = logging.getLogger(__name__)


class QuestionsService(BaseService):
    @return_service
    async def create_question(
        self,
        question_in: QuestionInCreate,
        questions_repo: QuestionsRepository,
        quizzes_repo: QuizzesRepository,
        options_repo: OptionsRepository,
    ):
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=question_in.quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        created_question = await questions_repo.create_question(question_in=question_in)

        if question_in.options:
            await options_repo.create_options_for_question(options_in=question_in.options, question_id=created_question.id)

        await questions_repo.connection.commit()
        question_with_options = await questions_repo.get_question_by_id(question_id=created_question.id)

        return QuestionResponse(
            message="Question created successfully.",
            data=QuestionOutData.model_validate(question_with_options),
        )

    @return_service
    async def get_question_by_id(
        self,
        question_id: int,
        questions_repo: QuestionsRepository,
    ):
        question = await questions_repo.get_question_by_id(question_id=question_id)
        if not question:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Question not found"},
            )

        return QuestionResponse(
            message="Question retrieved successfully.",
            data=QuestionOutData.model_validate(question),
        )

    @return_service
    async def get_questions_by_quiz_id(
        self,
        quiz_id: int,
        question_filters: QuestionFilters,
        questions_repo: QuestionsRepository,
        quizzes_repo: QuizzesRepository,
    ):
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        questions = await questions_repo.get_questions_by_quiz_id(quiz_id=quiz_id, skip=question_filters.skip, limit=question_filters.limit)

        return QuestionResponse(
            message="Questions retrieved successfully.",
            data=[QuestionOutData.model_validate(question) for question in questions],
        )

    @return_service
    async def get_all_questions(
        self,
        question_filters: QuestionFilters,
        questions_repo: QuestionsRepository,
    ):
        questions = await questions_repo.get_all_questions(skip=question_filters.skip, limit=question_filters.limit)

        return QuestionResponse(
            message="Questions retrieved successfully.",
            data=[QuestionOutData.model_validate(question) for question in questions],
        )

    @return_service
    async def update_question(
        self,
        question_id: int,
        question_in: QuestionInUpdate,
        questions_repo: QuestionsRepository,
        options_repo: OptionsRepository,
    ):
        question = await questions_repo.get_question_by_id(question_id=question_id)
        if not question:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Question not found"},
            )

        await questions_repo.update_question(question=question, question_in=question_in)

        if question_in.options is not None:
            await options_repo.delete_options_by_question_id(question_id=question_id)
            if question_in.options:
                await options_repo.create_options_for_question(options_in=question_in.options, question_id=question_id)

        question_with_options = await questions_repo.get_question_by_id(question_id=question_id)

        return QuestionResponse(
            message="Question updated successfully.",
            data=QuestionOutData.model_validate(question_with_options),
        )

    @return_service
    async def delete_question(
        self,
        question_id: int,
        questions_repo: QuestionsRepository,
    ):
        question = await questions_repo.get_question_by_id(question_id=question_id)
        if not question:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Question not found"},
            )

        await questions_repo.delete_question(question=question)

        return QuestionResponse(
            message="Question deleted successfully.",
            data=None,
        )
