from collections.abc import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import _get_connection_from_session
from app.services.base import BaseService


def get_service(service_type: type[BaseService]) -> Callable[[AsyncSession], BaseService]:
    def _get_service(
        session: AsyncSession = Depends(_get_connection_from_session),
    ) -> BaseService:
        return service_type(db=session)

    return _get_service
