from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.domain.enums.roles_enum import UserRole
from app.presentation.api.app_factory import create_app
from app.presentation.api.deps.auth_deps import get_current_user
from app.presentation.api.deps.user_deps import get_user_service


def _user_payload(
    *,
    first_name: str = "Andre",
    last_name: str = "Barbosa",
    date_of_birth: str = "1990-01-01",
    cpf: str = "12345678901",
    email: str = "andre@example.com",
    role: str = "CUSTOMER",
) -> dict:
    return {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth,
        "cpf": cpf,
        "email": email,
        "role": role,
    }


def _to_response(user: dict) -> dict:
    return {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "date_of_birth": user["date_of_birth"],
        "cpf": user["cpf"],
        "email": user["email"],
        "role": user["role"],
        "is_active": user["is_active"],
        "first_access": user["first_access"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }


class FakeUserService:
    def __init__(self) -> None:
        self._users: dict[int, dict] = {}
        self._next_id = 1

    def create(self, dto):
        now = datetime.now(timezone.utc)
        user = {
            "id": self._next_id,
            "first_name": dto.first_name,
            "last_name": dto.last_name,
            "date_of_birth": dto.date_of_birth,
            "cpf": dto.cpf,
            "email": str(dto.email),
            "role": dto.role,
            "is_active": True,
            "first_access": True,
            "created_at": now,
            "updated_at": now,
        }
        self._users[self._next_id] = user
        self._next_id += 1
        return _to_response(user)

    def get_all(self):
        return [_to_response(user) for user in self._users.values()]

    def get_by_id(self, user_id: int):
        user = self._users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return _to_response(user)

    def update(self, user_id: int, dto):
        user = self._users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user["first_name"] = dto.first_name
        user["last_name"] = dto.last_name
        user["date_of_birth"] = dto.date_of_birth
        user["cpf"] = dto.cpf
        user["email"] = str(dto.email)
        user["role"] = dto.role
        user["updated_at"] = datetime.now(timezone.utc)
        return _to_response(user)

    def delete(self, user_id: int):
        if user_id not in self._users:
            raise HTTPException(status_code=404, detail="User not found")
        del self._users[user_id]


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def fake_user_service():
    return FakeUserService()


@pytest.fixture
def client(app, fake_user_service):
    app.dependency_overrides[get_user_service] = lambda: fake_user_service
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


def _override_current_user(app, *, role: UserRole, first_access: bool):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=999,
        role=role,
        first_access=first_access,
        is_active=True,
    )


def _authenticate_admin(app):
    _override_current_user(app, role=UserRole.ADMIN, first_access=False)


def _create_user_for_test(client: TestClient) -> int:
    response = client.post("/users", json=_user_payload())
    assert response.status_code == 201
    return response.json()["id"]


def test_users_endpoints_require_authentication(client: TestClient):
    response = client.get("/users")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_user_requires_admin_role(client: TestClient, app):
    _override_current_user(app, role=UserRole.AGENT, first_access=False)

    response = client.post("/users", json=_user_payload())

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_first_access_user_is_blocked_by_password_policy(client: TestClient, app):
    _override_current_user(app, role=UserRole.ADMIN, first_access=True)

    response = client.get("/users")

    assert response.status_code == 403
    assert response.json()["detail"] == "Password change required"


def test_create_user_with_authenticated_admin(client: TestClient, app):
    _authenticate_admin(app)
    create_response = client.post("/users", json=_user_payload())
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] > 0
    assert created["email"] == "andre@example.com"


def test_list_users_with_authenticated_admin(client: TestClient, app):
    _authenticate_admin(app)
    _create_user_for_test(client)

    list_response = client.get("/users")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_get_user_by_id_with_authenticated_admin(client: TestClient, app):
    _authenticate_admin(app)
    user_id = _create_user_for_test(client)

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == user_id


def test_update_user_with_authenticated_admin(client: TestClient, app):
    _authenticate_admin(app)
    user_id = _create_user_for_test(client)

    update_response = client.put(
        f"/users/{user_id}",
        json=_user_payload(
            first_name="Maria",
            last_name="Silva",
            cpf="10987654321",
            email="maria@example.com",
            role="AGENT",
        ),
    )
    assert update_response.status_code == 200
    assert update_response.json()["first_name"] == "Maria"
    assert update_response.json()["email"] == "maria@example.com"


def test_delete_user_with_authenticated_admin(client: TestClient, app):
    _authenticate_admin(app)
    user_id = _create_user_for_test(client)

    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    get_after_delete = client.get(f"/users/{user_id}")
    assert get_after_delete.status_code == 404
    assert get_after_delete.json()["detail"] == "User not found"
