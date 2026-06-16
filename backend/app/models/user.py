from pydantic import BaseModel, EmailStr, Field

from app.core.roles import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=80)


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: Role = Role.USER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role = Role.USER

