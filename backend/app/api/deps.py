from typing import Annotated

from fastapi import Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import decode_access_token_user_id
from app.db.models import ClinicMembership, User
from app.db.session import get_db


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        user_id = decode_access_token_user_id(token)
    except JWTError:
        raise credentials_exception from None

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    if user.is_active is not True:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


def get_current_clinic_membership(
    clinic_id: Annotated[int, Path(gt=0, le=2147483647)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ClinicMembership:
    """Resolve the authenticated user's membership in the requested clinic."""
    statement = (
        select(ClinicMembership)
        .where(
            ClinicMembership.user_id == current_user.id,
            ClinicMembership.clinic_id == clinic_id,
        )
        .options(
            joinedload(ClinicMembership.clinic),
            selectinload(ClinicMembership.roles),
        )
        .execution_options(populate_existing=True)
    )
    membership = db.execute(statement).scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=404, detail="Clinic not found or inaccessible"
        )
    return membership
