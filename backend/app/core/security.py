# Security utilities for password hashing and token generation

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Encodes user identity and expiration into a signed JWT access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token_user_id(token: str) -> int:
    """Validate an access token and return its positive PostgreSQL Integer ID."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require_exp": True, "require_sub": True},
        )
    except (TypeError, ValueError, OverflowError) as exc:
        # Malformed claim types must also follow the JWTError contract.
        raise JWTError("Invalid token claims") from exc

    expiration = payload["exp"]
    if isinstance(expiration, bool) or not isinstance(expiration, (int, float)):
        raise JWTError("Invalid expiration")

    subject = payload["sub"]
    if (
        not isinstance(subject, str)
        or not 1 <= len(subject) <= 10
        or not subject.isascii()
        or not subject.isdecimal()
        or subject.startswith("0")
    ):
        raise JWTError("Invalid user ID")

    user_id = int(subject)
    if user_id > 2147483647:
        raise JWTError("Invalid user ID")
    return user_id
