from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel


if TYPE_CHECKING:
    from app.models.question import Question


class Option(RWModel, DateTimeModelMixin):
    __tablename__: str = "options"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        server_default=text("nextval('options_id_seq'::regclass)"),
    )
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    question: Mapped["Question"] = relationship("Question", back_populates="options")
