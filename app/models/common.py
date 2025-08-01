# common.py  (or wherever DateTimeModelMixin lives)

from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column


@declarative_mixin
class DateTimeModelMixin:
    # created_at is always present
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    # updated_at / deleted_at can be NULL
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
