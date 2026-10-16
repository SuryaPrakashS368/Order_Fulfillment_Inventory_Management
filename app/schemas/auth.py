from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )
    email: EmailStr
    password: str
    role: Optional[str] = "Customer"
 

class LoginRequest(BaseModel):

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):

    refresh_token: str


class LogoutRequest(BaseModel):

    refresh_token: str


class ChangePasswordRequest(BaseModel):

    current_password: str
    new_password: str


class UserResponse(BaseModel):

    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenResponse(BaseModel):

    access_token: str
    refresh_token: str
    token_type: str = "bearer"