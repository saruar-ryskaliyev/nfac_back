from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.quiz import Quiz
from app.models.tag import Tag
from app.models.user import User
from app.models.question import Question
from app.schemas.quiz import QuizInCreate, QuizInUpdate
from app.schemas.pagination import PaginationMeta
from datetime import datetime, timezone


class QuizzesRepository(BaseRepository):
    def __init__(self, conn: AsyncSession) -> None:
        super().__init__(conn)
    
    def _create_pagination_meta(self, total: int, skip: int, limit: int) -> PaginationMeta:
        current_page = (skip // limit) + 1
        total_pages = (total + limit - 1) // limit
        has_next = skip + limit < total
        has_previous = skip > 0
        
        return PaginationMeta(
            total=total,
            skip=skip,
            limit=limit,
            has_next=has_next,
            has_previous=has_previous,
            total_pages=total_pages,
            current_page=current_page,
        )

    @db_error_handler
    async def create_quiz(self, *, creator: User, quiz_in: QuizInCreate, tags: list[Tag] | None = None) -> Quiz:
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
    async def count_all_quizzes(self) -> int:
        query = select(func.count(Quiz.id)).where(Quiz.deleted_at.is_(None))
        raw_result = await self.connection.execute(query)
        return raw_result.scalar() or 0

    @db_error_handler
    async def count_public_quizzes(self) -> int:
        query = select(func.count(Quiz.id)).where(and_(Quiz.is_public, Quiz.deleted_at.is_(None)))
        raw_result = await self.connection.execute(query)
        return raw_result.scalar() or 0

    @db_error_handler
    async def count_quizzes_by_creator(self, *, creator_id: int) -> int:
        query = select(func.count(Quiz.id)).where(and_(Quiz.creator_id == creator_id, Quiz.deleted_at.is_(None)))
        raw_result = await self.connection.execute(query)
        return raw_result.scalar() or 0

    @db_error_handler
    async def count_quizzes_by_tag(self, *, tag: str) -> int:
        query = (
            select(func.count(Quiz.id))
            .join(Quiz.tags)
            .where(and_(Tag.name.ilike(f"%{tag}%"), Quiz.is_public, Quiz.deleted_at.is_(None)))
        )
        raw_result = await self.connection.execute(query)
        return raw_result.scalar() or 0

    @db_error_handler
    async def get_quiz_by_id(self, *, quiz_id: int) -> Quiz | None:
        query = select(Quiz).options(
            selectinload(Quiz.tags),
            selectinload(Quiz.questions).selectinload(Question.options)
        ).where(and_(Quiz.id == quiz_id, Quiz.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        if result is None:
            return None

        return result.Quiz

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
    async def get_all_quizzes_paginated(self, *, skip: int = 0, limit: int = 20) -> tuple[list[Quiz], PaginationMeta]:
        total = await self.count_all_quizzes()
        quizzes = await self.get_all_quizzes(skip=skip, limit=limit)
        meta = self._create_pagination_meta(total, skip, limit)
        return quizzes, meta

    @db_error_handler
    async def get_public_quizzes_paginated(self, *, skip: int = 0, limit: int = 20) -> tuple[list[Quiz], PaginationMeta]:
        total = await self.count_public_quizzes()
        quizzes = await self.get_public_quizzes(skip=skip, limit=limit)
        meta = self._create_pagination_meta(total, skip, limit)
        return quizzes, meta

    @db_error_handler
    async def get_quizzes_by_creator_paginated(self, *, creator_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Quiz], PaginationMeta]:
        total = await self.count_quizzes_by_creator(creator_id=creator_id)
        quizzes = await self.get_quizzes_by_creator(creator_id=creator_id, skip=skip, limit=limit)
        meta = self._create_pagination_meta(total, skip, limit)
        return quizzes, meta

    @db_error_handler
    async def search_quizzes_by_tag_paginated(self, *, tag: str, skip: int = 0, limit: int = 20) -> tuple[list[Quiz], PaginationMeta]:
        total = await self.count_quizzes_by_tag(tag=tag)
        quizzes = await self.search_quizzes_by_tag(tag=tag, skip=skip, limit=limit)
        meta = self._create_pagination_meta(total, skip, limit)
        return quizzes, meta

    @db_error_handler
    async def count_quizzes_by_text_search(self, *, search_text: str, public_only: bool = True) -> int:
        conditions = [
            or_(
                Quiz.title.ilike(f"%{search_text}%"),
                Quiz.description.ilike(f"%{search_text}%")
            ),
            Quiz.deleted_at.is_(None)
        ]
        
        if public_only:
            conditions.append(Quiz.is_public)
        
        query = select(func.count(Quiz.id)).where(and_(*conditions))
        raw_result = await self.connection.execute(query)
        return raw_result.scalar() or 0

    @db_error_handler
    async def search_quizzes_by_text(self, *, search_text: str, public_only: bool = True, skip: int = 0, limit: int = 100) -> list[Quiz]:
        conditions = [
            or_(
                Quiz.title.ilike(f"%{search_text}%"),
                Quiz.description.ilike(f"%{search_text}%")
            ),
            Quiz.deleted_at.is_(None)
        ]
        
        if public_only:
            conditions.append(Quiz.is_public)
        
        query = (
            select(Quiz)
            .options(selectinload(Quiz.tags))
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        
        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()
        
        return [result.Quiz for result in results]

    @db_error_handler
    async def search_quizzes_by_text_paginated(self, *, search_text: str, public_only: bool = True, skip: int = 0, limit: int = 20) -> tuple[list[Quiz], PaginationMeta]:
        total = await self.count_quizzes_by_text_search(search_text=search_text, public_only=public_only)
        quizzes = await self.search_quizzes_by_text(search_text=search_text, public_only=public_only, skip=skip, limit=limit)
        meta = self._create_pagination_meta(total, skip, limit)
        return quizzes, meta

    @db_error_handler
    async def update_quiz(self, *, quiz: Quiz, quiz_in: QuizInUpdate, tags: list[Tag] | None = None) -> Quiz:
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
        quiz.deleted_at = datetime.now(timezone.utc)

        await self.connection.commit()
        await self.connection.refresh(quiz)

        return quiz
