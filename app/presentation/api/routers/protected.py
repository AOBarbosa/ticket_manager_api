from fastapi import APIRouter, Depends
from app.presentation.api.deps.auth_deps import get_current_user

protected_router = APIRouter(dependencies=[Depends(get_current_user)])