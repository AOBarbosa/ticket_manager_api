from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.application.services.auth_service import AuthService
from app.presentation.api.deps.container import get_auth_service
from app.core.cookies import set_auth_cookies, clear_auth_cookies
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    must_change_password: bool

@router.post("/login", response_model=LoginResponse)
def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth: Annotated[AuthService, Depends(get_auth_service)],
):
    email = form_data.username
    try:
        pair = auth.login_with_email(email=email, password=form_data.password)
        set_auth_cookies(response, access_token=pair.access_token, refresh_token=pair.refresh_token)
        return LoginResponse(must_change_password=pair.must_change_password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(
    request: Request,
    response: Response,
    auth: Annotated[AuthService, Depends(get_auth_service)],
):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        new_access = auth.refresh_access_token(refresh_token)
        response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=new_access,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return AccessTokenResponse(access_token=new_access)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    auth: Annotated[AuthService, Depends(get_auth_service)],
):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)

    if refresh_token:
        try:
            auth.logout(refresh_token)
        except ValueError:
            pass

    clear_auth_cookies(response)
    return