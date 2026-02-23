from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.dtos.change_password_request import ChangePasswordRequest
from app.presentation.api.deps.auth_deps import get_current_user
from app.application.services.auth_service import AuthService
from app.presentation.api.deps.container import get_auth_service
from app.domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/change-password", status_code=204)
def change_password(
    body: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        auth.change_password(
            user_id=current_user.id,
            current_password=body.current_password,
            new_password=body.new_password,
            confirm_new_password=body.confirm_new_password,
        )
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
