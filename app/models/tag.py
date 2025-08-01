from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel

if TYPE_CHECKING:
    from app.models.quiz import Quiz


class Tag(RWModel, DateTimeModelMixin):
    __tablename__: str = "tags"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        server_default=text("nextval('tags_id_seq'::regclass)"),
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    quizzes: Mapped[list["Quiz"]] = relationship("Quiz", secondary="quiz_tags", back_populates="tags")