from typing import Annotated
from fastapi import APIRouter, Depends
from app.domain.dtos.user_dto import UserResponseDTO
from app.presentation.api.deps.auth_deps import get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/me", tags=["me"])

@router.get("", response_model=UserResponseDTO)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user