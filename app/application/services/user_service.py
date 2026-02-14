from app.domain.dtos.user_dto import CreateUserRequestDTO, UserResponseDTO
from app.domain.entities.user import User
from app.domain.mappers.users_mapper import UserMapper
from app.infra.repositories.user_repository import UserRepository

class UserService:
    """"
    Service class for managing User entities.
    """

    def __init__(self, repository: UserRepository, mapper: UserMapper) -> None:
        self.repository = repository
        self.mapper = mapper

    def create(self, dto: CreateUserRequestDTO) -> UserResponseDTO:
        user = self.mapper.to_entity(dto)

        saved = self.repository.create(user)

        user_dto = self.mapper.to_dto(saved)

        return user_dto

    def get_by_id(self, user_id: int) -> UserResponseDTO:
        user = self.repository.get_by_id(user_id)

        user_dto = self.mapper.to_dto(user)

        return user_dto
