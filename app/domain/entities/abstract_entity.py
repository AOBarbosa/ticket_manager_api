from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, func
from sqlmodel import SQLModel, Field


class AbstractEntity(SQLModel):
    id: int = Field(default=None, primary_key=True)

    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        nullable=False,
        sa_column_kwargs={"server_default": func.now()},
    )

    updated_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        nullable=False,
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )

    is_active: bool = Field(default=True, nullable=False)
