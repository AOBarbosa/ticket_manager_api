from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.dtos.user_dto import CreateUserRequestDTO, UserResponseDTO
from app.application.services.user_service import UserService
from app.presentation.api.deps import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponseDTO, status_code=201)
def create_user(body: CreateUserRequestDTO, service: UserService = Depends(get_user_service)):
    return service.create(body)


@router.get("", response_model=list[UserResponseDTO], status_code=status.HTTP_200_OK)
def list_users(service: UserService = Depends(get_user_service)):
    return service.get_all()


@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user_by_id(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_by_id(user_id)

    return user

@router.put("/{user_id}", response_model=UserResponseDTO)
def update_user(user_id: int, body: CreateUserRequestDTO, service: UserService = Depends(get_user_service)):
    user = service.update(user_id, body)
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    service.delete(user_id)


@router.get("/by-email", response_model=UserResponseDTO)
def get_user_by_email(email: str, service: UserService = Depends(get_user_service)):
    user = service.get_by_email(email)

    return user

@router.get("/by-cpf", response_model=UserResponseDTO)
def get_user_by_email(email: str, service: UserService = Depends(get_user_service)):
    user = service.get_by_cpf(email)

    return user
