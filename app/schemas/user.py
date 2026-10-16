from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


class AdminCreateUserRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )
    email: EmailStr
    password: str
    role: str


class UserUpdateRequest(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    email: EmailStr | None = None


class UserStatusRequest(BaseModel):

    is_active: bool


class UserResponse(BaseModel):

    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )