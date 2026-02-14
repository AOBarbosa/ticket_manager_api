from pydantic import EmailStr

from app.application.dto.user_dto import CreateUserRequestDTO, UserResponseDTO
from app.domain.entities.user import User
from app.infra.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def save(self, dto: CreateUserRequestDTO) -> UserResponseDTO:
        user = User(
            first_name=dto.first_name.strip(),
            last_name=dto.last_name.strip(),
            date_of_birth=dto.date_of_birth,
            cpf=dto.cpf.strip(),
            email=dto.email.strip().lower(),
            password=dto.password,
        )

        saved = self.repo.create(user)

        return UserResponseDTO(
            id=saved.id,
            first_name=saved.first_name,
            last_name=saved.last_name,
            date_of_birth=saved.date_of_birth,
            cpf=saved.cpf,
            email=saved.email,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )
