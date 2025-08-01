import logging

from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.database.repositories.answers import AnswersRepository
from app.database.repositories.questions import QuestionsRepository
from app.database.repositories.quiz_attempts import QuizAttemptsRepository
from app.database.repositories.quizzes import QuizzesRepository
from app.models.user import User
from app.schemas.answer import AnswerOutData, QuizResult, QuizResultResponse
from app.schemas.quiz_attempt import AttemptOutData, AttemptResponse
from app.services.base import BaseService
from app.utils import response_4xx, return_service

logger = logging.getLogger(__name__)


class QuizAttemptsService(BaseService):

    @return_service
    async def start_quiz_attempt(
        self,
        quiz_id: int,
        user: User,
        attempts_repo: QuizAttemptsRepository,
        quizzes_repo: QuizzesRepository,
    ):
        """Start a new quiz attempt"""

        # Verify quiz exists
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": f"Quiz {quiz_id} not found"},
            )

        # Check if user has an unfinished attempt
        existing_attempt = await attempts_repo.get_unfinished_attempt(
            user_id=user.id, quiz_id=quiz_id
        )

        if existing_attempt:
            # Return existing unfinished attempt
            return AttemptResponse(
                message="Continuing existing quiz attempt",
                data=AttemptOutData.model_validate(existing_attempt),
            )

        # Create new attempt
        attempt = await attempts_repo.create_attempt(quiz_id=quiz_id, user_id=user.id)
        await attempts_repo.connection.commit()

        return AttemptResponse(
            message="Quiz attempt started successfully",
            data=AttemptOutData.model_validate(attempt),
        )

    @return_service
    async def submit_quiz_attempt(
        self,
        attempt_id: int,
        user: User,
        attempts_repo: QuizAttemptsRepository,
        questions_repo: QuestionsRepository,
        answers_repo: AnswersRepository,
    ):
        """Submit/finish a quiz attempt and calculate score"""

        # Get the attempt
        attempt = await attempts_repo.get_attempt_by_id(attempt_id=attempt_id)
        if not attempt:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": f"Attempt {attempt_id} not found"},
            )

        # Verify ownership
        if attempt.user_id != user.id:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": "You can only submit your own attempts"},
            )

        # Check if already finished
        if attempt.finished_at:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": "This attempt has already been submitted"},
            )

        # Get all questions for this quiz
        quiz_questions = await questions_repo.get_questions_by_quiz_id(quiz_id=attempt.quiz_id)
        total_questions = len(quiz_questions)
        total_points = sum(q.points for q in quiz_questions)

        # Get all answers for this attempt
        answers = await answers_repo.get_answers_by_attempt(attempt_id=attempt_id)

        # Calculate score
        correct_answers = sum(1 for answer in answers if answer.is_correct)
        earned_points = sum(
            next((q.points for q in quiz_questions if q.id == answer.question_id), 0)
            for answer in answers if answer.is_correct
        )

        # Finish the attempt
        await attempts_repo.finish_attempt(attempt=attempt, score=earned_points)
        await attempts_repo.connection.commit()

        # Prepare quiz result
        quiz_result = QuizResult(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            user_id=attempt.user_id,
            attempt_no=attempt.attempt_no,
            total_questions=total_questions,
            correct_answers=correct_answers,
            total_points=earned_points,
            score_percentage=round((earned_points / total_points * 100), 2) if total_points > 0 else 0.0,
            answers=[AnswerOutData.model_validate(answer) for answer in answers],
        )

        return QuizResultResponse(
            message="Quiz attempt submitted successfully",
            data=quiz_result,
        )

    @return_service
    async def get_attempt_by_id(
        self,
        attempt_id: int,
        attempts_repo: QuizAttemptsRepository,
    ):
        """Get attempt details by ID"""

        attempt = await attempts_repo.get_attempt_by_id(attempt_id=attempt_id)
        if not attempt:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": f"Attempt {attempt_id} not found"},
            )

        return AttemptResponse(
            message="Attempt retrieved successfully",
            data=AttemptOutData.model_validate(attempt),
        )

    @return_service
    async def get_user_attempts_for_quiz(
        self,
        quiz_id: int,
        user: User,
        attempts_repo: QuizAttemptsRepository,
    ):
        """Get all attempts by user for a specific quiz"""

        attempts = await attempts_repo.get_user_attempts_for_quiz(
            user_id=user.id, quiz_id=quiz_id
        )

        return AttemptResponse(
            message="User attempts retrieved successfully",
            data=[AttemptOutData.model_validate(attempt) for attempt in attempts],
        )
