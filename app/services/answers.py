import logging

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.database.repositories.answers import AnswersRepository
from app.database.repositories.options import OptionsRepository
from app.database.repositories.questions import QuestionsRepository
from app.database.repositories.quizzes import QuizzesRepository
from app.models.user import User
from app.schemas.answer import (
    AnswerInCreate,
    AnswerOutData,
    AnswerResponse,
    AnswerSubmit,
    QuizResult,
    QuizResultResponse,
)
from app.services.base import BaseService
from app.utils import response_4xx, return_service

logger = logging.getLogger(__name__)


class AnswersService(BaseService):
    @return_service
    async def submit_answers_to_attempt(
        self,
        attempt_id: int,
        user: User,
        answers: list[AnswerSubmit],
        answers_repo: AnswersRepository,
        questions_repo: QuestionsRepository,
        options_repo: OptionsRepository,
):
        created_answers = []

        for answer_submit in answers:
            question = await questions_repo.get_question_by_id(question_id=answer_submit.question_id)
            if not question:
                return response_4xx(
                    status_code=HTTP_404_NOT_FOUND,
                    context={"reason": f"Question {answer_submit.question_id} not found"},
                )

            is_correct = None

            if question.question_type in ["single", "multiple"]:
                if not answer_submit.selected_option_ids:
                    return response_4xx(
                        status_code=HTTP_400_BAD_REQUEST,
                        context={"reason": f"Selected options required for question {answer_submit.question_id}"},
                    )

                question_options = await options_repo.get_options_by_question_id(question_id=answer_submit.question_id)
                correct_option_ids = {opt.id for opt in question_options if opt.is_correct}
                selected_option_ids = set(answer_submit.selected_option_ids)

                if question.question_type == "single":
                    is_correct = len(selected_option_ids) == 1 and selected_option_ids == correct_option_ids
                else:  # multiple
                    is_correct = selected_option_ids == correct_option_ids

            elif question.question_type == "text":
                if not answer_submit.text_answer:
                    return response_4xx(
                        status_code=HTTP_400_BAD_REQUEST,
                        context={"reason": f"Text answer required for question {answer_submit.question_id}"},
                    )

            answer_in = AnswerInCreate(
                attempt_id=attempt_id,
                question_id=answer_submit.question_id,
                selected_option_ids=answer_submit.selected_option_ids,
                text_answer=answer_submit.text_answer,
                is_correct=is_correct,
            )

            # Check if user already answered this question in this attempt
            existing_answer = await answers_repo.get_existing_answer(attempt_id=attempt_id, question_id=answer_submit.question_id)

            if existing_answer:
                # Update existing answer instead of creating new one
                updated_answer = await answers_repo.update_answer(answer=existing_answer, answer_in=answer_in)
                created_answers.append(updated_answer)
            else:
                # Create new answer
                created_answer = await answers_repo.create_answer(answer_in=answer_in)
                created_answers.append(created_answer)

        await answers_repo.connection.commit()

        return AnswerResponse(
            message="Answers submitted successfully.",
            data=[AnswerOutData.model_validate(answer) for answer in created_answers],
        )

    @return_service
    async def get_quiz_results(
        self,
        user_id: int,
        quiz_id: int,
        answers_repo: AnswersRepository,
        questions_repo: QuestionsRepository,
        quizzes_repo: QuizzesRepository,
):
        quiz = await quizzes_repo.get_quiz_by_id(quiz_id=quiz_id)
        if not quiz:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Quiz not found"},
            )

        answers = await answers_repo.get_answers_by_user_and_quiz(user_id=user_id, quiz_id=quiz_id)
        questions = await questions_repo.get_questions_by_quiz_id(quiz_id=quiz_id)

        total_questions = len(questions)
        correct_answers = sum(1 for answer in answers if answer.is_correct)
        total_points = sum(question.points for question in questions)
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0

        attempt_id = answers[0].attempt_id if answers else None
        if not attempt_id:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "No answers found for this quiz attempt"},
            )

        attempt_no = answers[0].quiz_attempt.attempt_no if answers and answers[0].quiz_attempt else 1

        quiz_result = QuizResult(
            quiz_id=quiz_id,
            user_id=user_id,
            total_questions=total_questions,
            correct_answers=correct_answers,
            total_points=total_points,
            score_percentage=score_percentage,
            answers=[AnswerOutData.model_validate(answer) for answer in answers],
            attempt_id=attempt_id,
            attempt_no=attempt_no,
        )

        return QuizResultResponse(
            message="Quiz results retrieved successfully.",
            data=quiz_result,
        )

    @return_service
    async def get_answer_by_id(
        self,
        answer_id: int,
        answers_repo: AnswersRepository,
):
        answer = await answers_repo.get_answer_by_id(answer_id=answer_id)
        if not answer:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Answer not found"},
            )

        return AnswerResponse(
            message="Answer retrieved successfully.",
            data=AnswerOutData.model_validate(answer),
        )
