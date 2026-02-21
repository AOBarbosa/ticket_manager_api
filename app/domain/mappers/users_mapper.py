from __future__ import annotations

from app.domain.dtos.user_dto import CreateUserRequestDTO, UserResponseDTO
from app.domain.entities.user import User
from app.infra.repositories.user_repository import UserRepository


class UserMapper:

    def to_entity(self, dto: CreateUserRequestDTO) -> User:
        """
        Maps CreateUserRequestDTO -> User (SQLModel entity).

        Notes:
          - Normalizes simple string fields (strip + lower email).
          - Password is passed through as-is (hash it in service/use-case before calling this,
            or adjust this mapper to accept a password_hash).
        """
        return User(
            first_name=dto.first_name.strip(),
            last_name=dto.last_name.strip(),
            date_of_birth=dto.date_of_birth,
            cpf=dto.cpf.strip(),
            email=str(dto.email).strip().lower(),
        )

    def to_dto(self, entity: User) -> UserResponseDTO:
        """
        Maps User (SQLModel entity) -> UserResponseDTO.

        Notes:
          - Does not expose password (response DTO doesn't contain it).
          - Assumes created_at/updated_at are present (server defaults).
        """
        return UserResponseDTO(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            date_of_birth=entity.date_of_birth,
            cpf=entity.cpf,
            email=entity.email,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
