from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, declared_attr

class RWModel(DeclarativeBase):          # SQLAlchemy 2.x base class
    __abstract__ = True                  # -- no own table

    # mark it as a *directive*, not a mapped attribute
    @declared_attr.directive
    def __tablename__(cls) -> str:       # cls is correct here, not self
        return cls.__name__.lower()
