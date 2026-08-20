# Security utilities for password hashing and token generation

from passlib.context import CryptContext

# Cryptographic context using bcrypt algorithm for secure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Verifies a plain text password against a hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Generates a secure hash of a plain text password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)