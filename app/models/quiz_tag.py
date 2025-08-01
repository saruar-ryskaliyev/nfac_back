from sqlalchemy import Integer, ForeignKey, Table, Column
from app.models.rwmodel import RWModel

quiz_tags = Table(
    "quiz_tags",
    RWModel.metadata,
    Column("quiz_id", Integer, ForeignKey("quizzes.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


