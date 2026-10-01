from datetime import timedelta
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.models import User
from app.db.session import get_db
from app.main import app


@pytest.fixture
def client_and_db():
    db = Mock(spec=Session)

    def override_get_db():
        yield db

    # Restore overrides even if a request or assertion fails.
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client, db
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def test_auth_me_returns_only_public_user_fields(client_and_db):
    client, db = client_and_db
    user = User(
        id=42,
        email="staff@example.com",
        full_name="Synthetic Staff User",
        hashed_password="synthetic-secret-password-hash",
        is_active=True,
        is_superuser=True,
    )
    db.get.return_value = user
    token = create_access_token({"sub": "42"})

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "email": user.email,
        "full_name": user.full_name,
        "id": user.id,
    }
    assert "hashed_password" not in response.text
    assert user.hashed_password not in response.text
    db.get.assert_called_once_with(User, 42)


@pytest.mark.parametrize("credential", ["missing", "invalid", "expired"])
def test_auth_me_rejects_credentials_without_lookup(client_and_db, credential):
    client, db = client_and_db
    headers = {}
    if credential == "invalid":
        headers["Authorization"] = "Bearer invalid-jwt"
    elif credential == "expired":
        token = create_access_token({"sub": "42"}, expires_delta=timedelta(minutes=-1))
        headers["Authorization"] = f"Bearer {token}"

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"
    db.get.assert_not_called()


def test_auth_me_rejects_nonexistent_user(client_and_db):
    client, db = client_and_db
    db.get.return_value = None
    token = create_access_token({"sub": "42"})

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"
    db.get.assert_called_once_with(User, 42)


@pytest.mark.parametrize("is_active", [False, None])
def test_auth_me_rejects_inactive_user(client_and_db, is_active):
    client, db = client_and_db
    db.get.return_value = User(id=42, is_active=is_active)
    token = create_access_token({"sub": "42"})

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Inactive user"}
    db.get.assert_called_once_with(User, 42)
