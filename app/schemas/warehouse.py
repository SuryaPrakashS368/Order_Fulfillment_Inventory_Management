from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class WarehouseCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=150
    )

    location: str = Field(
        min_length=2,
        max_length=255
    )

    capacity: int = Field(
        gt=0
    )


class WarehouseUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=255
    )

    capacity: int | None = Field(
        default=None,
        gt=0
    )


class WarehouseStatusUpdate(BaseModel):

    is_active: bool


class WarehouseResponse(BaseModel):

    id: int
    name: str
    location: str
    capacity: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class WarehouseUserResponse(BaseModel):

    id: int
    name: str
    email: str
    role: str
    is_active: bool