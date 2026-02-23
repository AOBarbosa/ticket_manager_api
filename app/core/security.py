from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

pwd_hasher = PasswordHash.recommended()
DUMMY_HASH = pwd_hasher.hash("dummypassword")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hasher.verify(plain_password, hashed_password)


def create_password_hash(password: str) -> str:
    return pwd_hasher.hash(password)


def create_access_token(*, sub: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    payload = {"sub": sub, "type": "access", "iat": int(now.timestamp()), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(*, sub: str, expires_days: int) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=expires_days)
    payload = {"sub": sub, "type": "refresh", "iat": int(now.timestamp()), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except InvalidTokenError as e:
        # opcional: normalize erro
        raise


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_dummy_on_missing_user(password: str) -> None:
    # hardening contra timing attacks
    verify_password(password, DUMMY_HASH)
