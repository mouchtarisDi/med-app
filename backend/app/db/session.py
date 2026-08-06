# Creates SQLAlchemy engine for Base and get_db() function, opening and closing 
# safely database sessions for each request

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create SQLAlchemy engine with pre-ping enabled to verify connections before using them
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Session factory for generating database sessions per API request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for defining ORM models
Base = declarative_base()

# FastAPI dependency providing a database session lifecycle (opens, yields, closes)
def get_db():
    """Dependency function to provide a database session for each request."""
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Yield the session to the request handler
    finally:
        db.close()  # Ensure the session is closed after the request is processed