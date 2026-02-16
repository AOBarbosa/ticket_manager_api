from typing import List

from app.domain.dtos.user_dto import CreateUserRequestDTO, UserResponseDTO
from app.domain.mappers.users_mapper import UserMapper
from app.application.validators.user_validator import UserValidator
from app.infra.repositories.user_repository import UserRepository
from app.domain.entities.user import User


class UserService:
    """
    Service class for managing User entities.
    """

    def __init__(self, repository: UserRepository, mapper: UserMapper, validator: UserValidator) -> None:
        self.repository = repository
        self.mapper = mapper
        self.validator = validator

    def create(self, dto: CreateUserRequestDTO) -> UserResponseDTO:
        user = self.mapper.to_entity(dto)

        user.email = str(user.email).strip().lower()
        user.cpf = "".join(ch for ch in user.cpf if ch.isdigit())

        self.validator.validate_create(user)

        saved = self.repository.create(user)

        return self.mapper.to_dto(saved)

    def get_all(self) -> list[UserResponseDTO]:
        users = self.repository.get_all()
        return [self.mapper.to_dto(user) for user in users]

    def get_by_id(self, user_id: int) -> UserResponseDTO:
        user = self.repository.get_by_id(user_id)
        self.validator.validate_found(user, not_found_detail="User not found")

        return self.mapper.to_dto(user)

    def update(self, user_id: int, dto: CreateUserRequestDTO) -> UserResponseDTO:
        existing_user = self.repository.get_by_id(user_id)
        self.validator.validate_found(existing_user, not_found_detail="User not found")

        existing_user.first_name = dto.first_name.strip()
        existing_user.last_name = dto.last_name.strip()
        existing_user.email = dto.email.strip().lower()
        existing_user.cpf = "".join(ch for ch in dto.cpf if ch.isdigit())

        self.validator.validate_update(existing_user)

        updated = self.repository.update(existing_user)

        return self.mapper.to_dto(updated)

    def delete(self, user_id: int) -> None:
        user = self.repository.get_by_id(user_id)
        self.validator.validate_found(user, not_found_detail="User not found")

        self.repository.delete(user_id)

    def get_by_email(self, email: str) -> UserResponseDTO:
        email_norm = email.strip().lower()
        user = self.repository.find_by_email(email_norm)
        self.validator.validate_found(user, not_found_detail="User not found")

        return self.mapper.to_dto(user)

    def get_by_cpf(self, cpf: str) -> UserResponseDTO:
        cpf_digits = "".join(ch for ch in cpf if ch.isdigit())
        user = self.repository.find_by_cpf(cpf_digits)
        self.validator.validate_found(user, not_found_detail="User not found")

        return self.mapper.to_dto(user)
