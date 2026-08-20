from pydantic import BaseModel

# Schema returned upon successful authentication containing JWT
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema representing payload stored inside the JWT token
class TokenData(BaseModel):
    email: str | None = None