from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.api.dependencies.auth import get_current_admin_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.questions import get_question_filters
from app.api.dependencies.service import get_service
from app.database.repositories.options import OptionsRepository
from app.database.repositories.questions import QuestionsRepository
from app.database.repositories.quizzes import QuizzesRepository
from app.models.user import User
from app.schemas.question import QuestionFilters, QuestionInCreate, QuestionInUpdate, QuestionResponse
from app.services.questions import QuestionsService
from app.utils import ERROR_RESPONSES

router = APIRouter()


@router.post(
    path="/",
    status_code=HTTP_201_CREATED,
    response_model=QuestionResponse,
    responses=ERROR_RESPONSES,
    name="questions:create",
)
async def create_question(
    *,
    questions_service: QuestionsService = Depends(get_service(QuestionsService)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    options_repo: OptionsRepository = Depends(get_repository(OptionsRepository)),
    question_in: QuestionInCreate,
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Create a new question.
    """
    result = await questions_service.create_question(
        question_in=question_in,
        questions_repo=questions_repo,
        quizzes_repo=quizzes_repo,
        options_repo=options_repo,
    )

    return await result.unwrap()


@router.get(
    path="/",
    status_code=HTTP_200_OK,
    response_model=QuestionResponse,
    responses=ERROR_RESPONSES,
    name="questions:get_all",
)
async def get_all_questions(
    *,
    questions_service: QuestionsService = Depends(get_service(QuestionsService)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    question_filters: QuestionFilters = Depends(get_question_filters),
):
    """
    Get all questions.
    """
    result = await questions_service.get_all_questions(
        question_filters=question_filters,
        questions_repo=questions_repo,
    )

    return await result.unwrap()


@router.get(
    path="/{question_id}",
    status_code=HTTP_200_OK,
    response_model=QuestionResponse,
    responses=ERROR_RESPONSES,
    name="questions:get_by_id",
)
async def get_question_by_id(
    *,
    question_id: int,
    questions_service: QuestionsService = Depends(get_service(QuestionsService)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
):
    """
    Get a question by ID.
    """
    result = await questions_service.get_question_by_id(
        question_id=question_id,
        questions_repo=questions_repo,
    )

    return await result.unwrap()


@router.get(
    path="/quiz/{quiz_id}",
    status_code=HTTP_200_OK,
    response_model=QuestionResponse,
    responses=ERROR_RESPONSES,
    name="questions:get_by_quiz_id",
)
async def get_questions_by_quiz_id(
    *,
    quiz_id: int,
    questions_service: QuestionsService = Depends(get_service(QuestionsService)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    question_filters: QuestionFilters = Depends(get_question_filters),
):
    """
    Get questions for a specific quiz.
    """
    result = await questions_service.get_questions_by_quiz_id(
        quiz_id=quiz_id,
        question_filters=question_filters,
        questions_repo=questions_repo,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.put(
    path="/{question_id}",
    status_code=HTTP_200_OK,
    response_model=QuestionResponse,
    responses=ERROR_RESPONSES,
    name="questions:update",
)
async def update_question(
    *,
    question_id: int,
    question_in: QuestionInUpdate,
    questions_service: QuestionsService = Depends(get_service(QuestionsService)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    options_repo: OptionsRepository = Depends(get_repository(OptionsRepository)),
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Update a question by ID (admin only).
    """
    result = await questions_service.update_question(
        question_id=question_id,
        question_in=question_in,
        questions_repo=questions_repo,
        options_repo=options_repo,
    )

    return await result.unwrap()


@router.delete(
    path="/{question_id}",
    status_code=HTTP_200_OK,
    name="questions:delete",
)
async def delete_question(
    *,
    question_id: int,
    questions_service: QuestionsService = Depends(get_service(QuestionsService)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Delete a question by ID (admin only).
    """
    result = await questions_service.delete_question(
        question_id=question_id,
        questions_repo=questions_repo,
    )

    return await result.unwrap()
