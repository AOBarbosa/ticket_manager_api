from fastapi import APIRouter, Depends
from app.presentation.api.deps.auth_deps import get_current_user
from app.presentation.api.deps.password_policy import enforce_password_change

protected_router = APIRouter(dependencies=[Depends(get_current_user), Depends(enforce_password_change)])