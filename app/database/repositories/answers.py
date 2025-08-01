from datetime import datetime, timezone
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.answer import Answer
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt
from app.schemas.answer import AnswerInCreate
from typing import Optional


class AnswersRepository(BaseRepository):
    def __init__(self, conn: AsyncSession) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_answer(self, *, answer_in: AnswerInCreate) -> Answer:
        answer = Answer(
            attempt_id=answer_in.attempt_id,
            question_id=answer_in.question_id,
            selected_option_ids=answer_in.selected_option_ids,
            text_answer=answer_in.text_answer,
            is_correct=answer_in.is_correct,
        )

        self.connection.add(answer)
        await self.connection.flush()

        return answer

    @db_error_handler
    async def get_existing_answer(self, *, attempt_id: int, question_id: int) -> Optional[Answer]:
        """Find existing answer by attempt and question"""
        query = select(Answer).where(
            and_(
                Answer.attempt_id == attempt_id, 
                Answer.question_id == question_id, 
                Answer.deleted_at.is_(None)
            )
        ).order_by(Answer.created_at.desc()).limit(1)

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        return result.Answer if result is not None else None

    @db_error_handler
    async def update_answer(self, *, answer: Answer, answer_in: AnswerInCreate) -> Answer:
        """Update existing answer with new data"""
        answer.selected_option_ids = answer_in.selected_option_ids
        answer.text_answer = answer_in.text_answer
        answer.is_correct = answer_in.is_correct
        answer.submitted_at = datetime.now(timezone.utc)
        
        await self.connection.flush()
        return answer

    @db_error_handler
    async def get_answer_by_id(self, *, answer_id: int) -> Optional[Answer]:
        query = select(Answer).options(selectinload(Answer.question), selectinload(Answer.quiz_attempt)).where(and_(Answer.id == answer_id, Answer.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

 
        return result.Answer if result is not None else result

    @db_error_handler
    async def get_answers_by_attempt(self, *, attempt_id: int) -> list[Answer]:
        """Get all answers for a specific attempt"""
        query = select(Answer).options(
            selectinload(Answer.question), 
            selectinload(Answer.quiz_attempt)
        ).where(
            and_(Answer.attempt_id == attempt_id, Answer.deleted_at.is_(None))
        )

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Answer for result in results]

    @db_error_handler
    async def get_all_answers(self, *, skip: int = 0, limit: int = 100) -> list[Answer]:
        query = select(Answer).options(selectinload(Answer.question), selectinload(Answer.quiz_attempt)).where(Answer.deleted_at.is_(None)).offset(skip).limit(limit)

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Answer for result in results]

    @db_error_handler
    async def get_answers_by_user_and_quiz(self, *, user_id: int, quiz_id: int) -> list[Answer]:
        """Get all answers by user for a specific quiz"""
        query = select(Answer).options(
            selectinload(Answer.question),
            selectinload(Answer.quiz_attempt)
        ).join(QuizAttempt).where(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id,
                Answer.deleted_at.is_(None)
            )
        )

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Answer for result in results]

    @db_error_handler
    async def delete_answer(self, *, answer: Answer) -> Answer:
        answer.deleted_at = datetime.now(timezone.utc)

        await self.connection.commit()
        await self.connection.refresh(answer)

        return answer
