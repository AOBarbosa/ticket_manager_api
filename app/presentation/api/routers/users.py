from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.dtos.user_dto import CreateUserRequestDTO, UserResponseDTO
from app.application.services.user_service import UserService
from app.domain.entities.user import User
from app.domain.enums.roles_enum import UserRole
from app.presentation.api.deps.permissions import require_roles
from app.presentation.api.deps.user_deps import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    body: CreateUserRequestDTO,
    service: Annotated[UserService, Depends(get_user_service)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
):
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

