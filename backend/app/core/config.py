import os

class Settings:
    """Application settings class reading configurations from environment variables."""
    # Database connection string pointing to the PostgreSQL container ('db')
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@db:5432/med_db"
    )

# Instantiate the settings object to be imported across the app
settings = Settings()