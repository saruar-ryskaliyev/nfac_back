from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
import enum

from app.core import security
from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"


class User(RWModel, DateTimeModelMixin):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('users_id_seq'::regclass)"),
    )
    username = Column(String(32), nullable=False, unique=True)
    email = Column(String(256), nullable=False, unique=True)
    salt = Column(String(255), nullable=False)
    hashed_password = Column(String(256), nullable=True)
    total_score = Column(Integer, nullable=False, server_default=text("0"))

    role = Column(
        SQLEnum(UserRole, name="userrole", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default=text("'student'")
    )
    quizzes = relationship("Quiz", back_populates="creator")

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)
