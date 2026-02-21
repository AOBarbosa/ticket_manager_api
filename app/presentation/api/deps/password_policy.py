from typing import Annotated
from fastapi import Depends, HTTPException, status, Request

from app.domain.entities.user import User
from app.presentation.api.deps.auth_deps import get_current_user

ALLOWED_PATHS_WHEN_FORCED = {
    "/auth/change-password",
    "/auth/logout",
    "/auth/refresh",
}

def enforce_password_change(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.first_access and request.url.path not in ALLOWED_PATHS_WHEN_FORCED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password change required",
        )
    return current_user