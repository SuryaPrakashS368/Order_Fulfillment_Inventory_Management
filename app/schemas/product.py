from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class ProductCreate(BaseModel):

    sku: str = Field(
        min_length=2,
        max_length=100
    )

    name: str = Field(
        min_length=2,
        max_length=200
    )

    description: str | None = None

    category_id: int = Field(
        gt=0
    )

    price: Decimal = Field(
        ge=0
    )

    cost_price: Decimal = Field(
        ge=0
    )


class ProductUpdate(BaseModel):

    sku: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200
    )

    description: str | None = None

    category_id: int | None = Field(
        default=None,
        gt=0
    )

    price: Decimal | None = Field(
        default=None,
        ge=0
    )

    cost_price: Decimal | None = Field(
        default=None,
        ge=0
    )


class ProductStatusUpdate(BaseModel):

    is_active: bool


class ProductResponse(BaseModel):

    id: int
    sku: str
    name: str
    description: str | None
    category_id: int
    price: Decimal
    cost_price: Decimal
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )