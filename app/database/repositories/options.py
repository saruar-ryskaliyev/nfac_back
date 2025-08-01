from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.option import Option
from app.schemas.option import OptionInCreate, OptionInUpdate


class OptionsRepository(BaseRepository):
    def __init__(self, conn: AsyncSession) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_option(self, *, option_in: OptionInCreate, question_id: int) -> Option:
        option = Option(
            question_id=question_id,
            option_text=option_in.option_text,
            is_correct=option_in.is_correct,
        )

        self.connection.add(option)
        await self.connection.commit()
        await self.connection.refresh(option)

        return option

    @db_error_handler
    async def create_options_for_question(self, *, options_in: list[OptionInCreate], question_id: int) -> list[Option]:
        options = []
        for option_in in options_in:
            option = Option(
                question_id=question_id,
                option_text=option_in.option_text,
                is_correct=option_in.is_correct,
            )
            options.append(option)
            self.connection.add(option)

        await self.connection.flush()

        return options

    @db_error_handler
    async def get_option_by_id(self, *, option_id: int) -> Option | None:
        query = select(Option).where(and_(Option.id == option_id, Option.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        if result is None:
            return None

        return result.Option

    @db_error_handler
    async def get_options_by_question_id(self, *, question_id: int) -> list[Option]:
        query = select(Option).where(and_(Option.question_id == question_id, Option.deleted_at.is_(None)))

        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        return [result.Option for result in results]

    @db_error_handler
    async def update_option(self, *, option: Option, option_in: OptionInUpdate) -> Option:
        if option_in.option_text is not None:
            option.option_text = option_in.option_text
        if option_in.is_correct is not None:
            option.is_correct = option_in.is_correct

        await self.connection.commit()
        await self.connection.refresh(option)

        return option

    @db_error_handler
    async def delete_options_by_question_id(self, *, question_id: int) -> None:
        query = select(Option).where(and_(Option.question_id == question_id, Option.deleted_at.is_(None)))
        raw_result = await self.connection.execute(query)
        results = raw_result.fetchall()

        for result in results:
            result.Option.deleted_at = func.now()

        await self.connection.commit()

    @db_error_handler
    async def delete_option(self, *, option: Option) -> Option:
        option.deleted_at = func.now()

        await self.connection.commit()
        await self.connection.refresh(option)

        return option
