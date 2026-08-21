from typing import Annotated

from pydantic import AfterValidator, Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_api_prefix(value: str) -> str:
    """Validate and normalize the configured API URL prefix."""
    value = value.strip()
    if not value.startswith("/"):
        raise ValueError("API_PREFIX must start with '/'")
    if value != "/":
        value = value.rstrip("/")
    return value


ApiPrefix = Annotated[str, AfterValidator(normalize_api_prefix)]


class Settings(BaseSettings):
    """Validated application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@db:5432/med_db",
        min_length=1,
    )
    SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = Field(default="HS256", min_length=1)
    ACCESS_TOKEN_EXPIRE_MINUTES: PositiveInt = 30
    API_PREFIX: ApiPrefix = "/api/v1"


settings = Settings()
