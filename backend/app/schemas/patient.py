"""Administrative Patient inputs and explicit public output."""

from datetime import date, datetime, timezone
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


ASCII_WHITESPACE = " \t\n\r\f\v"


class PatientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=25)
    email: EmailStr | None = Field(default=None, max_length=254)
    amka: str | None = Field(default=None, pattern=r"^[0-9]{11}$")
    date_of_birth: date | None = None

    @field_validator("first_name", "last_name", "phone", mode="before")
    @classmethod
    def trim_ascii(cls, value, info):
        if isinstance(value, str):
            value = value.strip(ASCII_WHITESPACE)
            if info.field_name == "phone" and not value:
                return None
        return value

    @field_validator("email", mode="before")
    @classmethod
    def bound_email(cls, value):
        if value is not None and (not isinstance(value, str) or len(value) > 254):
            raise ValueError("Invalid email")
        return value

    @field_validator("amka", mode="before")
    @classmethod
    def ascii_amka(cls, value):
        if value is not None and (
            not isinstance(value, str) or re.fullmatch(r"[0-9]{11}", value) is None
        ):
            raise ValueError("Invalid AMKA")
        return value

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def date_only(cls, value):
        if value is None:
            return None
        if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
            raise ValueError("Invalid date")
        parsed = date.fromisoformat(value)
        if parsed > datetime.now(timezone.utc).date():
            raise ValueError("Invalid date")
        return parsed


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    date_of_birth: date | None
    phone: str | None
    email: str | None
    created_at: datetime
    updated_at: datetime
