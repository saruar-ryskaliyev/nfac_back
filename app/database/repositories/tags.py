from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.tag import Tag
from app.schemas.tag import TagInCreate, TagInUpdate


class TagsRepository(BaseRepository):
    def __init__(self, conn: AsyncSession) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_tag(self, *, tag_in: TagInCreate) -> Tag:
        tag = Tag(
            name=tag_in.name,
        )

        self.connection.add(tag)
        await self.connection.commit()
        await self.connection.refresh(tag)

        return tag

    @db_error_handler
    async def get_tag_by_id(self, *, tag_id: int) -> Tag:
        query = select(Tag).where(and_(Tag.id == tag_id, Tag.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        return result.Tag if result is not None else result

    @db_error_handler
    async def get_tag_by_name(self, *, name: str) -> Tag | None:
        query = select(Tag).where(and_(Tag.name == name, Tag.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        return result.Tag if result is not None else None

    @db_error_handler
    async def get_all_tags(self, *, skip: int = 0, limit: int = 100) -> list[Tag]:
        query = select(Tag).where(Tag.deleted_at.is_(None)).offset(skip).limit(limit)

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Tag for result in results]

    @db_error_handler
    async def get_or_create_tags(self, *, tag_names: list[str]) -> list[Tag]:
        tags = []
        for name in tag_names:
            existing_tag = await self.get_tag_by_name(name=name)
            if existing_tag:
                tags.append(existing_tag)
            else:
                new_tag = await self.create_tag(tag_in=TagInCreate(name=name))
                tags.append(new_tag)
        return tags

    @db_error_handler
    async def update_tag(self, *, tag: Tag, tag_in: TagInUpdate) -> Tag:
        if tag_in.name is not None:
            tag.name = tag_in.name

        await self.connection.commit()
        await self.connection.refresh(tag)

        return tag

    @db_error_handler
    async def delete_tag(self, *, tag: Tag) -> Tag:
        tag.deleted_at = func.now()

        await self.connection.commit()
        await self.connection.refresh(tag)

        return tag