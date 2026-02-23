from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from app.domain.entities.refresh_token import RefreshToken
from app.infra.repositories.refresh_token_repository import RefreshTokenRepository


class RefreshTokenRepositoryImpl(RefreshTokenRepository):
    def __init__(self, session: Session):
        self.session = session

    def upsert_for_user(self, user_id: int, token_hash: str) -> None:
        existing = self.session.get(RefreshToken, user_id)
        now = datetime.now(timezone.utc)

        if existing:
            existing.token_hash = token_hash
            existing.revoked_at = None
            existing.updated_at = now
            self.session.add(existing)
        else:
            self.session.add(
                RefreshToken(
                    user_id=user_id,
                    token_hash=token_hash,
                    revoked_at=None,
                    updated_at=now,
                )
            )

        self.session.commit()

    def get_hash_for_user(self, user_id: int) -> Optional[str]:
        rt = self.session.get(RefreshToken, user_id)
        if rt is None or rt.revoked_at is not None:
            return None
        return rt.token_hash

    def revoke_for_user(self, user_id: int) -> None:
        rt = self.session.get(RefreshToken, user_id)
        if rt is None:
            return
        rt.revoked_at = datetime.now(timezone.utc)
        rt.updated_at = rt.revoked_at
        self.session.add(rt)
        self.session.commit()
