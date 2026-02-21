from fastapi import Response
from app.core.config import settings


def _cookie_common_kwargs() -> dict:
    common = dict(
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    if settings.COOKIE_DOMAIN:
        common["domain"] = settings.COOKIE_DOMAIN
    return common


def set_auth_cookies(response: Response, *, access_token: str, refresh_token: str) -> None:
    common = _cookie_common_kwargs()

    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **common,
    )

    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **common,
    )


def clear_auth_cookies(response: Response) -> None:
    common = {"path": "/"}
    if settings.COOKIE_DOMAIN:
        common["domain"] = settings.COOKIE_DOMAIN

    response.delete_cookie(settings.ACCESS_COOKIE_NAME, **common)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, **common)