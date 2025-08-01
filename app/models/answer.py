'''this is for answer model'''

from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel



if TYPE_CHECKING:
    from app.models.user import User
    from app.models.question import Question


class Answer(RWModel, DateTimeModelMixin):
    __tablename__: str = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    selected_option_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    text_answer: Mapped[str | None] = mapped_column(Text)
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="answers")

    
    def __init__(self, user_id: int, question_id: int, selected_option_ids: list[int] | None = None, text_answer: str | None = None, is_correct: bool | None = None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.question_id = question_id
        self.selected_option_ids = selected_option_ids
        self.text_answer = text_answer
        self.is_correct = is_correct