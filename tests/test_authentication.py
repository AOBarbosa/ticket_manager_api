from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from app.presentation.api.app_factory import create_app
from app.presentation.api.deps.container import get_auth_service


@dataclass(frozen=True)
class FakeTokenPair:
    access_token: str
    refresh_token: str
    must_change_password: bool = False


class FakeAuthService:
    def __init__(self) -> None:
        self.raise_login_error = False
        self.raise_refresh_error = False
        self.raise_logout_error = False
        self.logout_called_with: list[str] = []

    def login_with_email(self, email: str, password: str) -> FakeTokenPair:
        if self.raise_login_error:
            raise ValueError("Incorrect email or password")
        return FakeTokenPair(
            access_token=f"access-for-{email}",
            refresh_token=f"refresh-for-{email}",
            must_change_password=False,
        )

    def refresh_access_token(self, refresh_token: str) -> str:
        if self.raise_refresh_error:
            raise ValueError("Invalid refresh token")
        return f"new-access-from-{refresh_token}"

    def logout(self, refresh_token: str) -> None:
        self.logout_called_with.append(refresh_token)
        if self.raise_logout_error:
            raise ValueError("Invalid refresh token")


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def fake_auth_service():
    return FakeAuthService()


@pytest.fixture
def client(app, fake_auth_service):
    app.dependency_overrides[get_auth_service] = lambda: fake_auth_service
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


def test_login_success_sets_auth_cookies(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "secret"},
    )

    assert response.status_code == 200
    assert response.json() == {"must_change_password": False}
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert response.cookies["access_token"].strip('"') == "access-for-admin@example.com"
    assert response.cookies["refresh_token"].strip('"') == "refresh-for-admin@example.com"


def test_login_invalid_credentials_returns_401(
    client: TestClient, fake_auth_service: FakeAuthService
):
    fake_auth_service.raise_login_error = True

    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_refresh_without_cookie_returns_401(client: TestClient):
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_refresh_with_cookie_returns_new_access(client: TestClient):
    client.cookies.set("refresh_token", "rt-123")

    response = client.post("/auth/refresh")

    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access-from-rt-123"
    assert response.cookies.get("access_token") == "new-access-from-rt-123"


def test_refresh_invalid_token_returns_401(client: TestClient, fake_auth_service: FakeAuthService):
    fake_auth_service.raise_refresh_error = True
    client.cookies.set("refresh_token", "bad-rt")

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_logout_without_cookie_returns_204(client: TestClient):
    response = client.post("/auth/logout")

    assert response.status_code == 204


def test_logout_with_cookie_revokes_and_returns_204(
    client: TestClient, fake_auth_service: FakeAuthService
):
    client.cookies.set("refresh_token", "rt-logout")

    response = client.post("/auth/logout")

    assert response.status_code == 204
    assert fake_auth_service.logout_called_with == ["rt-logout"]
