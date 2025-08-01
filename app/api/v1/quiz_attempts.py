"""
Quiz Attempts API Endpoints

This module contains all API endpoints related to quiz attempts, including:
- Starting new quiz attempts
- Submitting/finishing attempts with score calculation
- Retrieving attempt details and history
- Managing user attempt data

All endpoints require authentication and follow RESTful conventions.
"""

from fastapi import APIRouter, Depends, Path
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.database import get_repository
from app.api.dependencies.service import get_service
from app.database.repositories.quiz_attempts import QuizAttemptsRepository
from app.database.repositories.quizzes import QuizzesRepository
from app.database.repositories.questions import QuestionsRepository
from app.database.repositories.answers import AnswersRepository
from app.models.user import User
from app.schemas.quiz_attempt import AttemptResponse, AttemptSubmission
from app.schemas.answer import QuizResultResponse
from app.services.quiz_attempts import QuizAttemptsService
from app.utils import ERROR_RESPONSES

router = APIRouter()


@router.post(
    path="/quizzes/{quiz_id}/start",
    status_code=HTTP_201_CREATED,
    response_model=AttemptResponse,
    responses=ERROR_RESPONSES,
    name="attempts:start_quiz",
    tags=["Quiz Attempts"],
    summary="Start a new quiz attempt",
    description="""
    **Start a new quiz attempt for the authenticated user.**
    
    This endpoint:
    - Creates a new quiz attempt record
    - Auto-increments the attempt number for this user/quiz combination
    - Returns the attempt ID that must be used when submitting answers
    - Checks if user already has an unfinished attempt for this quiz
    
    **Requirements:**
    - User must be authenticated
    - Quiz must exist and be accessible to the user
    - User cannot have an existing unfinished attempt for this quiz
    
    **Response includes:**
    - Attempt ID (required for answer submissions)
    - Quiz ID and attempt number
    - Started timestamp
    - Current score (initially 0)
    """,
)
async def start_quiz_attempt(
    *,
    quiz_id: int = Path(
        ...,
        description="ID of the quiz to start an attempt for",
        example=1,
        gt=0
    ),
    attempts_service: QuizAttemptsService = Depends(get_service(QuizAttemptsService)),
    attempts_repo: QuizAttemptsRepository = Depends(get_repository(QuizAttemptsRepository)),
    quizzes_repo: QuizzesRepository = Depends(get_repository(QuizzesRepository)),
    current_user: User = Depends(get_current_user_auth()),
):
    result = await attempts_service.start_quiz_attempt(
        quiz_id=quiz_id,
        user=current_user,
        attempts_repo=attempts_repo,
        quizzes_repo=quizzes_repo,
    )

    return await result.unwrap()


@router.post(
    path="/attempts/{attempt_id}/submit",
    status_code=HTTP_200_OK,
    response_model=QuizResultResponse,
    responses=ERROR_RESPONSES,
    name="attempts:submit_attempt",
    tags=["Quiz Attempts"],
    summary="Submit and finish a quiz attempt",
    description="""
    **Submit and finalize a quiz attempt.**
    
    This endpoint:
    - Marks the attempt as finished with a completion timestamp
    - Calculates the final score based on correct answers
    - Returns detailed quiz results including score breakdown
    - Updates user's total score if applicable
    
    **Requirements:**
    - User must be authenticated and own the attempt
    - Attempt must exist and not be already finished
    - All required answers should be submitted before finishing
    
    **Request Body:**
    - Empty JSON object `{}` (just triggers the submission)
    
    **Response includes:**
    - Final score and percentage
    - Number of correct/incorrect answers
    - Total questions attempted
    - Detailed breakdown of each question and answer
    - Time taken to complete the quiz
    """,
)
async def submit_quiz_attempt(
    *,
    attempt_id: int = Path(
        ...,
        description="ID of the quiz attempt to submit/finish",
        example=1,
        gt=0
    ),
    submission: AttemptSubmission,  # Empty body to trigger submission
    attempts_service: QuizAttemptsService = Depends(get_service(QuizAttemptsService)),
    attempts_repo: QuizAttemptsRepository = Depends(get_repository(QuizAttemptsRepository)),
    questions_repo: QuestionsRepository = Depends(get_repository(QuestionsRepository)),
    answers_repo: AnswersRepository = Depends(get_repository(AnswersRepository)),
    current_user: User = Depends(get_current_user_auth()),
):
    result = await attempts_service.submit_quiz_attempt(
        attempt_id=attempt_id,
        user=current_user,
        attempts_repo=attempts_repo,
        questions_repo=questions_repo,
        answers_repo=answers_repo,
    )

    return await result.unwrap()


@router.get(
    path="/attempts/{attempt_id}",
    status_code=HTTP_200_OK,
    response_model=AttemptResponse,
    responses=ERROR_RESPONSES,
    name="attempts:get_by_id",
    tags=["Quiz Attempts"],
    summary="Get quiz attempt details by ID",
    description="""
    **Retrieve detailed information about a specific quiz attempt.**
    
    This endpoint:
    - Returns attempt metadata (ID, quiz ID, user ID, attempt number)
    - Shows timing information (started/finished timestamps)
    - Displays current or final score
    - Includes related quiz and user information
    
    **Requirements:**
    - User must be authenticated
    - Attempt must exist
    - Can view any attempt (useful for reviewing past attempts)
    
    **Response includes:**
    - Attempt ID and attempt number
    - Associated quiz and user information
    - Start and finish timestamps
    - Current score (0 if unfinished, calculated score if finished)
    - Attempt status (finished/unfinished)
    """,
)
async def get_attempt_by_id(
    *,
    attempt_id: int = Path(
        ...,
        description="ID of the quiz attempt to retrieve",
        example=1,
        gt=0
    ),
    attempts_service: QuizAttemptsService = Depends(get_service(QuizAttemptsService)),
    attempts_repo: QuizAttemptsRepository = Depends(get_repository(QuizAttemptsRepository)),
):
    result = await attempts_service.get_attempt_by_id(
        attempt_id=attempt_id,
        attempts_repo=attempts_repo,
    )

    return await result.unwrap()


@router.get(
    path="/quizzes/{quiz_id}/attempts",
    status_code=HTTP_200_OK,
    response_model=AttemptResponse,
    responses=ERROR_RESPONSES,
    name="attempts:get_user_attempts",
    tags=["Quiz Attempts"],
    summary="Get all user attempts for a specific quiz",
    description="""
    **Retrieve all quiz attempts by the current user for a specific quiz.**
    
    This endpoint:
    - Returns all attempts made by the authenticated user for the specified quiz
    - Ordered by attempt number (first attempt to latest attempt)
    - Includes both finished and unfinished attempts
    - Useful for showing user's quiz history and progress
    
    **Requirements:**
    - User must be authenticated
    - Quiz must exist
    - Only returns attempts for the current user (privacy protection)
    
    **Response includes:**
    - Array of attempt objects
    - Each attempt contains: ID, attempt number, timestamps, scores
    - Finished status for each attempt
    - Complete attempt history for the user on this quiz
    
    **Use cases:**
    - Show user their quiz attempt history
    - Display progress tracking
    - Allow user to review past performance
    - Check if user has unfinished attempts
    """,
)
async def get_user_attempts_for_quiz(
    *,
    quiz_id: int = Path(
        ...,
        description="ID of the quiz to get user attempts for",
        example=1,
        gt=0
    ),
    attempts_service: QuizAttemptsService = Depends(get_service(QuizAttemptsService)),
    attempts_repo: QuizAttemptsRepository = Depends(get_repository(QuizAttemptsRepository)),
    current_user: User = Depends(get_current_user_auth()),
):
    result = await attempts_service.get_user_attempts_for_quiz(
        quiz_id=quiz_id,
        user=current_user,
        attempts_repo=attempts_repo,
    )

    return await result.unwrap()