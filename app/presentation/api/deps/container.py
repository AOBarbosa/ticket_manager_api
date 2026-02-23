from typing import Generator
from fastapi import Depends
from sqlmodel import Session

from app.core.db.engine import engine  # adapte pro seu engine
from app.domain.mappers.users_mapper import UserMapper
from app.infra.repositories.user_repository_impl import UserRepositoryImpl
from app.infra.repositories.refresh_token_repository_impl import RefreshTokenRepositoryImpl
from app.application.services.auth_service import AuthService


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    user_repo = UserRepositoryImpl(session)
    refresh_repo = RefreshTokenRepositoryImpl(session)
    user_mapper = UserMapper()
    return AuthService(users=user_repo, refresh_tokens=refresh_repo, mapper=user_mapper)
