from __future__ import annotations

from dataclasses import dataclass

from jwt.exceptions import InvalidTokenError

from app.core.security import (
    verify_password,
    verify_dummy_on_missing_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token,
)
from app.core.config import settings
from app.domain.dtos.user_dto import UserResponseDTO
from app.domain.entities.user import User
from app.domain.mappers.users_mapper import UserMapper
from app.infra.repositories.user_repository import UserRepository
from app.infra.repositories.refresh_token_repository import RefreshTokenRepository


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    def __init__(self, users: UserRepository, refresh_tokens: RefreshTokenRepository, mapper: UserMapper):
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

        return TokenPair(access_token=access, refresh_token=refresh)

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

        return create_access_token(sub=str(user_id), expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    def get_user_from_access_token(self, access_token: str) -> UserResponseDTO:
        try:
            payload = decode_token(access_token)
        except InvalidTokenError:
            raise ValueError("Could not validate credentials")

        if payload.get("type") != "access":
            raise ValueError("Invalid access token type")

        sub = payload.get("sub")
        if not sub or not str(sub).isdigit():
            raise ValueError("Could not validate credentials")

        user = self.users.get_by_id(int(sub))
        if user is None:
            raise ValueError("Could not validate credentials")

        user_dto = self.mapper.to_dto(user)

        return user_dto