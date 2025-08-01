from datetime import datetime, timezone
from sqlalchemy import and_, select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.quiz_attempt import QuizAttempt


class QuizAttemptsRepository(BaseRepository):
    def __init__(self, conn: AsyncSession) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_attempt(self, *, quiz_id: int, user_id: int) -> QuizAttempt:
        """Create a new quiz attempt with auto-incremented attempt_no"""
        
        # Get the next attempt number for this user/quiz combination
        next_attempt_query = select(func.coalesce(func.max(QuizAttempt.attempt_no), 0) + 1).where(
            and_(QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == user_id)
        )
        result = await self.connection.execute(next_attempt_query)
        attempt_no = result.scalar() 

        if attempt_no is None:
            attempt_no = 1
        
        # Create the attempt
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=user_id,
            attempt_no=attempt_no,
        )
        
        self.connection.add(attempt)
        await self.connection.flush()
        
        return attempt

    @db_error_handler
    async def get_attempt_by_id(self, *, attempt_id: int) -> Optional[QuizAttempt]:
        """Get attempt by ID with relationships loaded"""
        query = select(QuizAttempt).options(
            selectinload(QuizAttempt.quiz),
            selectinload(QuizAttempt.user),
            selectinload(QuizAttempt.answers)
        ).where(and_(QuizAttempt.id == attempt_id, QuizAttempt.deleted_at.is_(None)))
        
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        
        return result.QuizAttempt if result is not None else None

    @db_error_handler
    async def get_user_attempts_for_quiz(self, *, user_id: int, quiz_id: int) -> list[QuizAttempt]:
        """Get all attempts by a user for a specific quiz, ordered by attempt_no"""
        query = select(QuizAttempt).where(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.deleted_at.is_(None)
            )
        ).order_by(QuizAttempt.attempt_no)
        
        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()
        
        return [result.QuizAttempt for result in results]

    @db_error_handler
    async def get_latest_attempt(self, *, user_id: int, quiz_id: int) -> Optional[QuizAttempt]:
        """Get the latest attempt by a user for a quiz"""
        query = select(QuizAttempt).where(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.deleted_at.is_(None)
            )
        ).order_by(desc(QuizAttempt.attempt_no)).limit(1)
        
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        
        return result.QuizAttempt if result is not None else None

    @db_error_handler
    async def finish_attempt(self, *, attempt: QuizAttempt, score: int) -> QuizAttempt:
        """Mark an attempt as finished with a score"""
        attempt.finished_at = datetime.now(timezone.utc)
        attempt.score = score
        
        await self.connection.flush()
        return attempt

    @db_error_handler
    async def get_unfinished_attempt(self, *, user_id: int, quiz_id: int) -> Optional[QuizAttempt]:
        """Get any unfinished attempt for this user/quiz"""
        query = select(QuizAttempt).where(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.finished_at.is_(None),
                QuizAttempt.deleted_at.is_(None)
            )
        ).order_by(desc(QuizAttempt.created_at)).limit(1)
        
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        
        return result.QuizAttempt if result is not None else None