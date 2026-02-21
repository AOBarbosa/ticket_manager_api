from __future__ import annotations

from typing import Optional
from fastapi import HTTPException, status
from pydantic import validate_email

from app.application.utils.validation_utils import is_valid_cpf_digits
from app.domain.entities.user import User
from app.infra.repositories.user_repository import UserRepository


class UserValidator:
    """
    FastAPI-doc-like approach:
    - raise HTTPException for 4xx
    - service remains exception-free
    """

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def validate_found(
        self, user: Optional[User], *, not_found_detail: str = "Resource not found"
    ) -> None:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail
            )

    def validate_create(self, user: User) -> None:
        if not user.first_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="first_name is required"
            )
        if not user.last_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="last_name is required"
            )
        if not user.cpf.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="cpf is required"
            )
        if not user.date_of_birth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="date_of_birth is required",
            )
        if not user.password_hash.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="password is required"
            )

        new_email = str(user.email).strip().lower()
        self.__validate_email(new_email)

        normalized_cpf = "".join(ch for ch in user.cpf if ch.isdigit())
        user.cpf = normalized_cpf
        self.__validate_cpf(user.cpf)

    def validate_update(self, user: User) -> None:
        existing_email = self.repo.find_by_email(user.email)
        if existing_email is not None and existing_email.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="email already exists"
            )

        existing_cpf = self.repo.find_by_cpf(user.cpf)
        if existing_cpf is not None and existing_cpf.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="cpf already exists"
            )

    def __validate_email(self, email_to_validate: str) -> None:
        if not validate_email(email_to_validate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="email is invalid"
            )

        existing_email = self.repo.find_by_email(email_to_validate)
        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="E-mail already exists"
            )

    def __validate_cpf(self, cpf_to_validate: str) -> None:
        if not is_valid_cpf_digits(cpf_to_validate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF is invalid",
            )

        existing_cpf = self.repo.find_by_cpf(cpf_to_validate)
        if existing_cpf is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF already exists",
            )
