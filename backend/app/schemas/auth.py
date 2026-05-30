from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "student"

    @validator("role")
    def valid_role(cls, v):
        if v not in ("student", "teacher"):
            raise ValueError("role phải là student hoặc teacher")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    avatar_url: str = ""
    role: str = "student"
    is_admin: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


TokenResponse.update_forward_refs()
