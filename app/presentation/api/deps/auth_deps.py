from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.application.services.auth_service import AuthService
from app.domain.dtos.user_dto import UserResponseDTO
from app.presentation.api.deps.container import get_auth_service
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


def _get_token_from_request(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if creds and creds.scheme.lower() == "bearer" and creds.credentials:
        return creds.credentials

    cookie_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Annotated[str, Depends(_get_token_from_request)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponseDTO:
    try:
        return auth.get_user_from_access_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Could not validate credentials: {e}")
