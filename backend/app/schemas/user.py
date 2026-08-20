# Pydantic Schemas validate the data received from the user and filter what 
# is returnd by the API

from pydantic import BaseModel, EmailStr

# Shared properties across all user schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

# Schema required when registering a new user (receives plain password)
class UserCreate(UserBase):
    password: str

# Schema used for returning user data (omits sensitive password field)
class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True