"""Quiz Attempt Model - tracks individual quiz runs/sessions"""

from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.quiz import Quiz
    from app.models.answer import Answer


class QuizAttempt(RWModel, DateTimeModelMixin):
    __tablename__: str = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False)

    # Unique constraint to prevent duplicate attempt numbers
    __table_args__ = (
        UniqueConstraint("quiz_id", "user_id", "attempt_no", name="uq_quiz_user_attempt"),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="quiz_attempts")
    quiz: Mapped["Quiz"] = relationship(back_populates="attempts")  
    answers: Mapped[list["Answer"]] = relationship(back_populates="quiz_attempt")

    def __init__(self, quiz_id: int, user_id: int, attempt_no: int, **kwargs):
        super().__init__(**kwargs)
        self.quiz_id = quiz_id
        self.user_id = user_id
        self.attempt_no = attempt_no
        # Set default score if not provided
        if 'score' not in kwargs:
            self.score = 0