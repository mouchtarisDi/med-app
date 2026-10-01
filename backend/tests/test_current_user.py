import asyncio
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.api.deps import get_current_user, oauth2_scheme
from app.core.security import create_access_token
from app.db.models import User


def test_current_user_returns_active_user():
    user = User(id=42, is_active=True)
    db = Mock(spec=Session)
    db.get.return_value = user
    token = create_access_token({"sub": "42"})
    request = Request({
        "type": "http",
        "headers": [(b"authorization", f"Bearer {token}".encode())],
    })
    extracted_token = asyncio.run(oauth2_scheme(request))

    result = get_current_user(token=extracted_token, db=db)

    assert result is user
    db.get.assert_called_once_with(User, 42)


@pytest.mark.parametrize(
    "authorization",
    [None, "Basic synthetic-credentials", "Bearer", "Bearer ", "Bearer invalid-jwt"],
    ids=["missing", "wrong-scheme", "empty", "empty-with-space", "invalid-jwt"],
)
def test_current_user_rejects_invalid_credentials_without_lookup(authorization):
    headers = [] if authorization is None else [
        (b"authorization", authorization.encode())
    ]
    request = Request({"type": "http", "headers": headers})
    token = asyncio.run(oauth2_scheme(request))
    db = Mock(spec=Session)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    db.get.assert_not_called()


def test_current_user_rejects_nonexistent_user():
    db = Mock(spec=Session)
    db.get.return_value = None
    token = create_access_token({"sub": "42"})

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    db.get.assert_called_once_with(User, 42)


@pytest.mark.parametrize("is_active", [False, None])
def test_current_user_rejects_inactive_user(is_active):
    db = Mock(spec=Session)
    db.get.return_value = User(id=42, is_active=is_active)
    token = create_access_token({"sub": "42"})

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"
    db.get.assert_called_once_with(User, 42)


def test_current_user_propagates_database_failure():
    db = Mock(spec=Session)
    database_error = OperationalError("SELECT", {}, Exception("Synthetic failure"))
    db.get.side_effect = database_error
    token = create_access_token({"sub": "42"})

    with pytest.raises(OperationalError) as exc_info:
        get_current_user(token=token, db=db)

    assert exc_info.value is database_error
    db.get.assert_called_once_with(User, 42)
