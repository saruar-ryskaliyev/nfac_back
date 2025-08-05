from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.message import ApiResponse
from app.schemas.question import QuestionOutData
from app.schemas.answer import AnswerOutData


class AttemptCreate(BaseModel):
    """Schema for creating a new quiz attempt"""
    quiz_id: int = Field(
        ...,
        description="ID of the quiz to attempt",
        example=1,
        gt=0
    )


class AttemptBase(BaseModel):
    """Base schema for quiz attempt data"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "quiz_id": 1,
                "user_id": 1,
                "attempt_no": 1,
                "score": 85,
                "started_at": "2025-08-01T12:00:00Z",
                "finished_at": "2025-08-01T12:15:30Z"
            }
        }
    )

    id: int = Field(
        ...,
        description="Unique identifier for the quiz attempt",
        example=1
    )
    quiz_id: int = Field(
        ...,
        description="ID of the associated quiz",
        example=1
    )
    user_id: int = Field(
        ...,
        description="ID of the user who made this attempt",
        example=1
    )
    attempt_no: int = Field(
        ...,
        description="Sequential attempt number for this user/quiz combination (1, 2, 3, etc.)",
        example=1,
        ge=1
    )
    score: int = Field(
        ...,
        description="Current score (0 for unfinished attempts, calculated score for finished attempts)",
        example=85,
        ge=0
    )
    started_at: datetime = Field(
        ...,
        description="Timestamp when the attempt was started",
        example="2025-08-01T12:00:00Z"
    )
    finished_at: datetime | None = Field(
        None,
        description="Timestamp when the attempt was finished (null for ongoing attempts)",
        example="2025-08-01T12:15:30Z"
    )


class AttemptOutData(AttemptBase):
    """Output schema for quiz attempt data in API responses"""
    pass


class AttemptResponse(ApiResponse):
    """API response wrapper for quiz attempt data"""
    message: str = Field(
        default="Quiz Attempt API Response",
        description="Response message describing the operation result"
    )
    data: AttemptOutData | list[AttemptOutData] | None = Field(
        None,
        description="Quiz attempt data (single object or array depending on endpoint)"
    )
    detail: dict[str, Any] | None = Field(
        None,
        description="Additional details about the response",
        example={"attempt_created": True, "next_attempt_number": 2}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "Quiz attempt started successfully",
                    "data": {
                        "id": 1,
                        "quiz_id": 1,
                        "user_id": 1,
                        "attempt_no": 1,
                        "score": 0,
                        "started_at": "2025-08-01T12:00:00Z",
                        "finished_at": None
                    },
                    "detail": {
                        "attempt_created": True,
                        "next_attempt_number": 2
                    }
                },
                {
                    "message": "User attempts retrieved successfully",
                    "data": [
                        {
                            "id": 1,
                            "quiz_id": 1,
                            "user_id": 1,
                            "attempt_no": 1,
                            "score": 85,
                            "started_at": "2025-08-01T11:00:00Z",
                            "finished_at": "2025-08-01T11:15:30Z"
                        },
                        {
                            "id": 2,
                            "quiz_id": 1,
                            "user_id": 1,
                            "attempt_no": 2,
                            "score": 0,
                            "started_at": "2025-08-01T12:00:00Z",
                            "finished_at": None
                        }
                    ],
                    "detail": {
                        "total_attempts": 2,
                        "finished_attempts": 1,
                        "best_score": 85
                    }
                }
            ]
        }
    )


class AttemptSubmission(BaseModel):
    """Schema for submitting/finishing a quiz attempt"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {},
            "description": "Empty object - no additional data needed to finish an attempt"
        }
    )
    
    # No additional fields needed - just triggers the finish/grading process
    # The empty body serves as an explicit action to finalize the attempt


class AttemptDetailData(AttemptBase):
    """Enhanced attempt data with questions, options, and user answers"""
    questions: list[QuestionOutData] = Field(
        default_factory=list,
        description="List of questions in this quiz with their options"
    )
    user_answers: list[AnswerOutData] = Field(
        default_factory=list,
        description="User's submitted answers for this attempt"
    )


class AttemptDetailResponse(ApiResponse):
    """API response for detailed attempt information including questions and answers"""
    message: str = Field(
        default="Attempt details retrieved successfully",
        description="Response message describing the operation result"
    )
    data: AttemptDetailData | None = Field(
        None,
        description="Detailed attempt data with questions and user answers"
    )
    detail: dict[str, Any] | None = Field(
        None,
        description="Additional details about the response"
    )