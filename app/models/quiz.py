from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel


class Quiz(RWModel, DateTimeModelMixin):
    __tablename__ = "quizzes"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('quizzes_id_seq'::regclass)"),
    )
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, nullable=False, server_default=text("true"))

    creator = relationship("User", back_populates="quizzes")