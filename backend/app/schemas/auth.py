from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_admin: bool

    class Config:
        orm_mode = True


TokenResponse.update_forward_refs()
