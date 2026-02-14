from fastapi import APIRouter, Depends
from app.domain.dtos.user_dto import CreateUserRequestDTO, UserResponseDTO
from app.application.services.user_service import UserService
from app.presentation.api.deps import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserResponseDTO, status_code=201)
def create_user(body: CreateUserRequestDTO, service: UserService = Depends(get_user_service)):
    return service.create(body)

@router.get("", response_model=list[UserResponseDTO])
def list_users(limit: int = 50, offset: int = 0, service: UserService = Depends(get_user_service)):
    users = service.repository.get_all()
    return [
        UserResponseDTO(
            id=u.id, first_name=u.first_name, last_name=u.last_name,
            date_of_birth=u.date_of_birth, cpf=u.cpf, email=u.email,
            created_at=u.created_at, updated_at=u.updated_at
        )
        for u in users
    ]

@router.get(f"/{id}", response_model=UserResponseDTO)
def get_user_by_id(user_id: int, service: UserService = Depends(get_user_service)):
    return service.get_by_id(user_id)
