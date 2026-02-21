from fastapi import Depends
from sqlmodel import Session

from app.core.db.session import get_session
from app.infra.repositories.user_repository_impl import UserRepositoryImpl
from app.domain.mappers.users_mapper import UserMapper
from app.application.validators.user_validator import UserValidator
from app.application.services.user_service import UserService


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    repo = UserRepositoryImpl(session)
    mapper = UserMapper()
    validator = UserValidator(repo)
    return UserService(repo, mapper, validator)
