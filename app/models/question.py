from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.answer import Answer
    from app.models.option import Option


class Question(RWModel, DateTimeModelMixin):
    __tablename__: str = "questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        server_default=text("nextval('questions_id_seq'::regclass)"),
    )
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    options: Mapped[list[Option]] = relationship("Option", back_populates="question")
    answers: Mapped[list[Answer]] = relationship("Answer", back_populates="question")
