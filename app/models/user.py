from typing import TYPE_CHECKING
import enum

from sqlalchemy import Integer, String, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core import security
from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.quiz_attempt import QuizAttempt

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"


class User(RWModel, DateTimeModelMixin):
    __tablename__: str = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        server_default=text("nextval('users_id_seq'::regclass)"),
    )
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    salt: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=True)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="userrole", values_callable=lambda x: [e.value for e in x]), nullable=False, server_default=text("'student'"))
    quizzes: Mapped[list["Quiz"]] = relationship("Quiz", back_populates="creator")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship("QuizAttempt", back_populates="user")

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)
