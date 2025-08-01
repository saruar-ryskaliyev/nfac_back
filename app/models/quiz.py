from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.user import User
    from app.models.quiz_attempt import QuizAttempt


class Quiz(RWModel, DateTimeModelMixin):
    __tablename__: str = "quizzes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        server_default=text("nextval('quizzes_id_seq'::regclass)"),
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    creator: Mapped["User"] = relationship("User", back_populates="quizzes")
    questions: Mapped[list[Question]] = relationship("Question", back_populates="quiz")
    attempts: Mapped[list["QuizAttempt"]] = relationship("QuizAttempt", back_populates="quiz")
