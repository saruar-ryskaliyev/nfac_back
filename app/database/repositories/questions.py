from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.question import Question
from app.schemas.question import QuestionInCreate, QuestionInUpdate


class QuestionsRepository(BaseRepository):
    def __init__(self, conn: AsyncSession) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_question(self, *, question_in: QuestionInCreate) -> Question:
        question = Question(
            quiz_id=question_in.quiz_id,
            question_text=question_in.question_text,
            question_type=question_in.question_type,
            points=question_in.points,
        )

        self.connection.add(question)
        await self.connection.flush()

        return question

    @db_error_handler
    async def get_question_by_id(self, *, question_id: int) -> Question | None:
        from app.models.option import Option

        query = select(Question).options(selectinload(Question.options.and_(Option.deleted_at.is_(None)))).where(and_(Question.id == question_id, Question.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        if result is None:
            return None

        return result.Question if result is not None else result

    @db_error_handler
    async def get_questions_by_quiz_id(self, *, quiz_id: int, skip: int = 0, limit: int = 100) -> list[Question]:
        from app.models.option import Option

        query = (
            select(Question).options(selectinload(Question.options.and_(Option.deleted_at.is_(None)))).where(and_(Question.quiz_id == quiz_id, Question.deleted_at.is_(None))).offset(skip).limit(limit)
        )

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Question for result in results]

    @db_error_handler
    async def get_all_questions(self, *, skip: int = 0, limit: int = 100) -> list[Question]:
        from app.models.option import Option

        query = select(Question).options(selectinload(Question.options.and_(Option.deleted_at.is_(None)))).where(Question.deleted_at.is_(None)).offset(skip).limit(limit)

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Question for result in results]

    @db_error_handler
    async def update_question(self, *, question: Question, question_in: QuestionInUpdate) -> Question:
        if question_in.question_text is not None:
            question.question_text = question_in.question_text
        if question_in.question_type is not None:
            question.question_type = question_in.question_type
        if question_in.points is not None:
            question.points = question_in.points

        await self.connection.commit()
        await self.connection.refresh(question)

        return question

    @db_error_handler
    async def delete_question(self, *, question: Question) -> Question:
        question.deleted_at = func.now()

        await self.connection.commit()
        await self.connection.refresh(question)

        return question
