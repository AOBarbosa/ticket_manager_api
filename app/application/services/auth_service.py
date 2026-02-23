from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass

from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from app.core.security import (
    verify_password,
    verify_dummy_on_missing_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token,
    create_password_hash,
)
from app.core.config import settings
from app.domain.dtos.user_dto import UserResponseDTO
from app.domain.mappers.users_mapper import UserMapper
from app.infra.repositories.user_repository import UserRepository
from app.infra.repositories.refresh_token_repository import RefreshTokenRepository


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    must_change_password: bool = False


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        mapper: UserMapper,
    ):
        self.users = users
        self.refresh_tokens = refresh_tokens
        self.mapper = mapper

    def login_with_email(self, email: str, password: str) -> TokenPair:
        user = self.users.find_by_email(email)

        if not user:
            verify_dummy_on_missing_user(password)
            raise ValueError("Incorrect email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Incorrect email or password")

        access = create_access_token(
            sub=str(user.id), expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        refresh = create_refresh_token(
            sub=str(user.id), expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        self.refresh_tokens.upsert_for_user(user.id, hash_refresh_token(refresh))

        return TokenPair(
            access_token=access, refresh_token=refresh, must_change_password=user.first_access
        )

    def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise ValueError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        sub = payload.get("sub")
        if not sub or not str(sub).isdigit():
            raise ValueError("Invalid token subject")

        user_id = int(sub)

        self.refresh_tokens.revoke_for_user(user_id)

    def refresh_access_token(self, refresh_token: str) -> str:
        try:
            payload = decode_token(refresh_token)
        except InvalidTokenError:
            raise ValueError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token type")

        sub = payload.get("sub")
        if not sub or not str(sub).isdigit():
            raise ValueError("Invalid refresh token subject")

        user_id = int(sub)
        stored_hash = self.refresh_tokens.get_hash_for_user(user_id)
        if stored_hash is None:
            raise ValueError("Refresh token revoked")

        if hash_refresh_token(refresh_token) != stored_hash:
            raise ValueError("Refresh token mismatch")

        return create_access_token(
            sub=str(user_id), expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    def get_user_from_access_token(self, token: str) -> UserResponseDTO:
        try:
            payload = decode_token(token)
        except ExpiredSignatureError:
            raise ValueError("token expired")
        except InvalidTokenError:
            raise ValueError("invalid token")

        if payload.get("type") != "access":
            raise ValueError("invalid token type")

        sub = payload.get("sub")
        if not sub:
            raise ValueError("missing sub")

        try:
            user_id = int(sub)
        except (TypeError, ValueError):
            raise ValueError("invalid sub")

        user_dto = self.mapper.to_dto(self.users.get_by_id(user_id))
        if not user_dto:
            raise ValueError("user not found")

        if not user_dto.is_active:
            raise ValueError("inactive user")

        return user_dto

    def change_password(
        self, *, user_id: int, current_password: str, new_password: str, confirm_new_password: str
    ) -> None:
        user = self.users.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        if not new_password == confirm_new_password:
            raise ValueError("New password is incorrect")

        user.password_hash = create_password_hash(new_password)
        user.first_access = False
        user.password_changed_at = datetime.now(timezone.utc)

        self.users.update(user)
