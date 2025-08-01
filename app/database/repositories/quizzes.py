from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.quiz import Quiz
from app.models.tag import Tag
from app.models.user import User
from app.schemas.quiz import QuizInCreate, QuizInUpdate


class QuizzesRepository(BaseRepository):
    def __init__(self, conn: AsyncSession) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_quiz(self, *, creator: User, quiz_in: QuizInCreate, tags: list[Tag] = None) -> Quiz:
        quiz = Quiz(
            title=quiz_in.title,
            description=quiz_in.description,
            creator_id=creator.id,
            is_public=quiz_in.is_public,
        )

        if tags:
            quiz.tags = tags

        self.connection.add(quiz)
        await self.connection.commit()
        await self.connection.refresh(quiz, ["tags"])

        return quiz

    @db_error_handler
    async def get_quiz_by_id(self, *, quiz_id: int) -> Quiz:
        query = select(Quiz).options(selectinload(Quiz.tags)).where(and_(Quiz.id == quiz_id, Quiz.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        return result.Quiz if result is not None else result

    @db_error_handler
    async def get_all_quizzes(self, *, skip: int = 0, limit: int = 100) -> list[Quiz]:
        query = select(Quiz).options(selectinload(Quiz.tags)).where(Quiz.deleted_at.is_(None)).offset(skip).limit(limit)

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Quiz for result in results]

    @db_error_handler
    async def get_public_quizzes(self, *, skip: int = 0, limit: int = 100) -> list[Quiz]:
        query = select(Quiz).options(selectinload(Quiz.tags)).where(and_(Quiz.is_public, Quiz.deleted_at.is_(None))).offset(skip).limit(limit)

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Quiz for result in results]

    @db_error_handler
    async def get_quizzes_by_creator(self, *, creator_id: int, skip: int = 0, limit: int = 100) -> list[Quiz]:
        query = select(Quiz).options(selectinload(Quiz.tags)).where(and_(Quiz.creator_id == creator_id, Quiz.deleted_at.is_(None))).offset(skip).limit(limit)

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Quiz for result in results]

    @db_error_handler
    async def search_quizzes_by_tag(self, *, tag: str, skip: int = 0, limit: int = 100) -> list[Quiz]:
        query = (
            select(Quiz)
            .join(Quiz.tags)
            .options(selectinload(Quiz.tags))
            .where(and_(Tag.name.ilike(f"%{tag}%"), Quiz.is_public, Quiz.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
        )

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Quiz for result in results]

    @db_error_handler
    async def update_quiz(self, *, quiz: Quiz, quiz_in: QuizInUpdate, tags: list[Tag] = None) -> Quiz:
        if quiz_in.title is not None:
            quiz.title = quiz_in.title
        if quiz_in.description is not None:
            quiz.description = quiz_in.description
        if quiz_in.is_public is not None:
            quiz.is_public = quiz_in.is_public
        if tags is not None:
            quiz.tags = tags

        await self.connection.commit()
        await self.connection.refresh(quiz, ["tags"])

        return quiz

    @db_error_handler
    async def delete_quiz(self, *, quiz: Quiz) -> Quiz:
        quiz.deleted_at = func.now()

        await self.connection.commit()
        await self.connection.refresh(quiz)

        return quiz
