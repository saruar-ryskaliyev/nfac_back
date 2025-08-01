from datetime import datetime, timezone
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.answer import Answer
from app.models.question import Question
from app.schemas.answer import AnswerInCreate
from typing import Optional


class AnswersRepository(BaseRepository):
    def __init__(self, conn: AsyncSession) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_answer(self, *, answer_in: AnswerInCreate) -> Answer:
        answer = Answer(
            user_id=answer_in.user_id,
            question_id=answer_in.question_id,
            selected_option_ids=answer_in.selected_option_ids,
            text_answer=answer_in.text_answer,
            is_correct=answer_in.is_correct,
        )

        self.connection.add(answer)
        await self.connection.flush()

        return answer

    @db_error_handler
    async def get_answer_by_id(self, *, answer_id: int) -> Optional[Answer]:
        query = select(Answer).options(selectinload(Answer.question), selectinload(Answer.user)).where(and_(Answer.id == answer_id, Answer.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

 
        return result.Answer if result is not None else result

    @db_error_handler
    async def get_answers_by_user_and_quiz(self, *, user_id: int, quiz_id: int) -> list[Answer]:
        query = (
            select(Answer)
            .join(Question, Answer.question_id == Question.id)
            .options(selectinload(Answer.question), selectinload(Answer.user))
            .where(and_(Answer.user_id == user_id, Question.quiz_id == quiz_id, Answer.deleted_at.is_(None)))
        )

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Answer for result in results]

    @db_error_handler
    async def get_answers_by_user(self, *, user_id: int, skip: int = 0, limit: int = 100) -> list[Answer]:
        query = select(Answer).options(selectinload(Answer.question), selectinload(Answer.user)).where(and_(Answer.user_id == user_id, Answer.deleted_at.is_(None))).offset(skip).limit(limit)

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Answer for result in results]

    @db_error_handler
    async def get_all_answers(self, *, skip: int = 0, limit: int = 100) -> list[Answer]:
        query = select(Answer).options(selectinload(Answer.question), selectinload(Answer.user)).where(Answer.deleted_at.is_(None)).offset(skip).limit(limit)

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Answer for result in results]

    @db_error_handler
    async def delete_answer(self, *, answer: Answer) -> Answer:
        answer.deleted_at = datetime.now(timezone.utc)

        await self.connection.commit()
        await self.connection.refresh(answer)

        return answer
