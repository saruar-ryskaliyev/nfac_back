from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.api.dependencies.auth import get_current_admin_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.quizzes import get_quiz_filters
from app.api.dependencies.service import get_service
from app.database.repositories.quizzes import QuizzesRepository
from app.database.repositories.tags import TagsRepository
from app.database.repositories.questions import QuestionsRepository
from app.database.repositories.options import OptionsRepository
from app.models.user import User
from app.schemas.quiz import QuizFilters, QuizInCreate, QuizInUpdate, QuizResponse, QuizDetailResponse, QuizPaginatedResponse, LeaderboardResponse, QuizGenerateRequest
from app.services.quizzes import QuizzesService
# GeminiAIService will be imported when needed
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
    tags_repo: TagsRepository = Depends(get_repository(TagsRepository)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    options_repo: OptionsRepository = Depends(get_repository(OptionsRepository)),
    quiz_in: QuizInCreate,
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Create a new quiz with optional questions and options.
    """
    result = await quizzes_service.create_quiz(
        creator=current_user,
        quiz_in=quiz_in,
        quizzes_repo=quizzes_repo,
        tags_repo=tags_repo,
        questions_repo=questions_repo,
        options_repo=options_repo,
    )

    return await result.unwrap()


@router.post(
    path="/generate",
    status_code=HTTP_201_CREATED,
    response_model=QuizResponse,
    responses=ERROR_RESPONSES,
    name="quizzes:generate",
)
async def generate_quiz(
    *,
    request: QuizGenerateRequest,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    tags_repo: TagsRepository = Depends(get_repository(TagsRepository)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    options_repo: OptionsRepository = Depends(get_repository(OptionsRepository)),
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Generate a quiz using AI based on the provided prompt.
    """
    from app.services.gemini_ai import GeminiAIService
    gemini_service = GeminiAIService()
    
    ai_quiz_data = await gemini_service.generate_quiz_from_prompt(
        prompt=request.prompt,
        num_questions=request.num_questions
    )
    
    from app.schemas.question import QuestionInQuizCreate
    from app.schemas.option import OptionInCreate
    
    questions = []
    for question_data in ai_quiz_data.questions:
        options = [
            OptionInCreate(
                option_text=option_text,
                is_correct=(i == question_data.correct_answer)
            )
            for i, option_text in enumerate(question_data.options)
        ]
        
        questions.append(
            QuestionInQuizCreate(
                question_text=question_data.question_text,
                question_type="single",
                options=options
            )
        )
    
    quiz_in = QuizInCreate(
        title=ai_quiz_data.title,
        description=ai_quiz_data.description,
        is_public=request.is_public,
        tag_names=request.tag_names,
        questions=questions
    )
    
    result = await quizzes_service.create_quiz(
        creator=current_user,
        quiz_in=quiz_in,
        quizzes_repo=quizzes_repo,
        tags_repo=tags_repo,
        questions_repo=questions_repo,
        options_repo=options_repo,
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
    path="/search",
    status_code=HTTP_200_OK,
    response_model=QuizPaginatedResponse,
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
    Search quizzes by text (title/description) or tag. 
    - Use 'search' parameter for text search in quiz titles and descriptions
    - Use 'tag' parameter for tag-based search
    - If no parameters provided, returns all public quizzes
    """
    result = await quizzes_service.search_quizzes(
        quiz_filters=quiz_filters,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.get(
    path="/{quiz_id}",
    status_code=HTTP_200_OK,
    response_model=QuizDetailResponse,
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
    Get a quiz by ID with all questions and their options.
    """
    result = await quizzes_service.get_quiz_by_id(
        quiz_id=quiz_id,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.get(
    path="/user/{user_id}",
    status_code=HTTP_200_OK,
    response_model=QuizPaginatedResponse,
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
    tags_repo: TagsRepository = Depends(get_repository(TagsRepository)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    options_repo: OptionsRepository = Depends(get_repository(OptionsRepository)),
    current_user: User = Depends(get_current_admin_user()),
):
    """
    Update a quiz by ID (admin only). Questions can be optionally updated.
    """
    result = await quizzes_service.update_quiz(
        quiz_id=quiz_id,
        quiz_in=quiz_in,
        quizzes_repo=quizzes_repo,
        tags_repo=tags_repo,
        questions_repo=questions_repo,
        options_repo=options_repo,
    )

    return await result.unwrap()


@router.get(
    path="/{quiz_id}/leaderboard",
    status_code=HTTP_200_OK,
    response_model=LeaderboardResponse,
    responses=ERROR_RESPONSES,
    name="quizzes:get_leaderboard",
)
async def get_quiz_leaderboard(
    *,
    quiz_id: int,
    quizzes_service: QuizzesService = Depends(get_service(QuizzesService)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
):
    """
    Get the leaderboard for a specific quiz showing top scoring attempts.
    """
    result = await quizzes_service.get_quiz_leaderboard(
        quiz_id=quiz_id,
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
