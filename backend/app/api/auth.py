# Authentication API endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut
from app.db.models.user import User
from app.core.security import get_password_hash

# Router dedicated to authentication operations
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user after verifying email uniqueness and hashing the password."""
    # Check if a user with the provided email already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash plain text password before storing it in the database
    hashed_pw = get_password_hash(user_in.password)

    # Create new db record instance
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pw
    )

    # Commit to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user