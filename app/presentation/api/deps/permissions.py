from typing import Annotated
from fastapi import Depends, HTTPException, status

from app.domain.entities.user import User
from app.domain.enums.roles_enum import UserRole
from app.presentation.api.deps.auth_deps import get_current_user

def require_roles(*allowed_roles: UserRole):
    def dependency(current_user: Annotated[User, Depends(get_current_user)]):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user
    return dependency