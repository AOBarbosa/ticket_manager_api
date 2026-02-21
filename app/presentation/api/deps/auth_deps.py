from typing import Annotated
from fastapi import Depends, HTTPException, Request, status

from app.application.services.auth_service import AuthService
from app.domain.dtos.user_dto import UserResponseDTO
from app.presentation.api.deps.container import get_auth_service
from app.core.config import settings

def get_current_user(
    request: Request,
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponseDTO:
    token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        return auth.get_user_from_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )