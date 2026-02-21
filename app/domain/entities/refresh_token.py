from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    user_id: int = Field(primary_key=True, index=True)
    token_hash: str = Field(index=True)
    revoked_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))