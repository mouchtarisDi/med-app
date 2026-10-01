from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.api import auth
from app.core.config import settings
from app.core.security import decode_access_token_user_id
from app.db.models import User


def test_successful_login_uses_user_id_as_jwt_subject(monkeypatch):
    user = User(
        id=42,
        email="login-subject@example.invalid",
        hashed_password="synthetic-unused-password-hash",
        full_name="Synthetic Login User",
    )
    db = Mock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = user
    verify_password = Mock(return_value=True)
    monkeypatch.setattr(auth, "verify_password", verify_password)
    form_data = OAuth2PasswordRequestForm(
        username=user.email, password="synthetic-login-password"
    )

    response = auth.login_for_access_token(form_data=form_data, db=db)

    verify_password.assert_called_once_with(
        form_data.password, user.hashed_password
    )
    assert response["token_type"] == "bearer"
    assert isinstance(response["access_token"], str)
    assert response["access_token"]
    payload = jwt.decode(
        response["access_token"],
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert payload["sub"] == str(user.id)
    assert isinstance(payload["sub"], str)
    assert "exp" in payload
    assert set(payload) == {"sub", "exp"}


def test_decode_access_token_returns_integer_user_id():
    token = jwt.encode(
        {"sub": "42", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    user_id = decode_access_token_user_id(token)

    assert user_id == 42
    assert type(user_id) is int


@pytest.mark.parametrize(
    "invalid_subject",
    [None, 42, "", "staff@example.invalid", "0", "-1", "1.5", " 42", "+42",
     "042", "٤٢", "2147483648", "9" * 100],
)
def test_decode_access_token_rejects_invalid_subject(invalid_subject):
    token = jwt.encode(
        {"sub": invalid_subject, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(JWTError):
        decode_access_token_user_id(token)


@pytest.mark.parametrize("missing_claim", ["sub", "exp"])
def test_decode_access_token_requires_subject_and_expiration(missing_claim):
    payload = {"sub": "42", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    del payload[missing_claim]
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    with pytest.raises(JWTError):
        decode_access_token_user_id(token)


@pytest.mark.parametrize("expiration", [0, None, "invalid", True])
def test_decode_access_token_rejects_expired_or_invalid_expiration(expiration):
    token = jwt.encode(
        {"sub": "42", "exp": expiration},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(JWTError):
        decode_access_token_user_id(token)


def test_decode_access_token_rejects_invalid_signature():
    token = jwt.encode(
        {"sub": "42", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        settings.SECRET_KEY + "-different-test-key",
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(JWTError):
        decode_access_token_user_id(token)
