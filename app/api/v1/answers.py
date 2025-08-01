from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.database import get_repository
from app.api.dependencies.service import get_service
from app.database.repositories.answers import AnswersRepository
from app.database.repositories.options import OptionsRepository
from app.database.repositories.questions import QuestionsRepository
from app.database.repositories.quizzes import QuizzesRepository
from app.models.user import User
from app.schemas.answer import AnswerResponse, AnswerSubmit, QuizResultResponse
from app.services.answers import AnswersService
from app.utils import ERROR_RESPONSES

router = APIRouter()


@router.post(
    path="/attempts/{attempt_id}/answers",
    status_code=HTTP_201_CREATED,
    response_model=AnswerResponse,
    responses=ERROR_RESPONSES,
    name="answers:submit_to_attempt",
)
async def submit_answers_to_attempt(
    *,
    attempt_id: int,
    answers_service: AnswersService = Depends(get_service(AnswersService)),
    answers_repo: AnswersRepository = Depends(get_repository(AnswersRepository)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    options_repo: OptionsRepository = Depends(get_repository(OptionsRepository)),
    answers: list[AnswerSubmit],
    current_user: User = Depends(get_current_user_auth()),
):
    """
    Submit answers for questions within a specific attempt.
    """
    result = await answers_service.submit_answers_to_attempt(
        attempt_id=attempt_id,
        user=current_user,
        answers=answers,
        answers_repo=answers_repo,
        questions_repo=questions_repo,
        options_repo=options_repo,
    )

    return await result.unwrap()


@router.get(
    path="/results/{quiz_id}",
    status_code=HTTP_200_OK,
    response_model=QuizResultResponse,
    responses=ERROR_RESPONSES,
    name="answers:get_quiz_results",
)
async def get_quiz_results(
    *,
    quiz_id: int,
    answers_service: AnswersService = Depends(get_service(AnswersService)),
    answers_repo: AnswersRepository = Depends(get_repository(AnswersRepository)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    current_user: User = Depends(get_current_user_auth()),
):
    """
    Get results for a quiz.
    """
    result = await answers_service.get_quiz_results(
        user_id=current_user.id,
        quiz_id=quiz_id,
        answers_repo=answers_repo,
        questions_repo=questions_repo,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.get(
    path="/{answer_id}",
    status_code=HTTP_200_OK,
    response_model=AnswerResponse,
    responses=ERROR_RESPONSES,
    name="answers:get_by_id",
)
async def get_answer_by_id(
    *,
    answer_id: int,
    answers_service: AnswersService = Depends(get_service(AnswersService)),
    answers_repo: AnswersRepository = Depends(get_repository(AnswersRepository)),
    current_user: User = Depends(get_current_user_auth()),
):
    """
    Get an answer by ID.
    """
    result = await answers_service.get_answer_by_id(
        answer_id=answer_id,
        answers_repo=answers_repo,
    )

    return await result.unwrap()
