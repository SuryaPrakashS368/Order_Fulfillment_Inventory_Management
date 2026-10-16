from pydantic import BaseModel, ConfigDict, Field


class InventoryCreate(BaseModel):

    product_id: int = Field(
        gt=0
    )

    warehouse_id: int = Field(
        gt=0
    )

    available_quantity: int = Field(
        default=0,
        ge=0
    )

    reorder_level: int = Field(
        default=0,
        ge=0
    )


class InventoryUpdate(BaseModel):

    reorder_level: int = Field(
        ge=0
    )


class InventoryResponse(BaseModel):

    id: int
    product_id: int
    warehouse_id: int
    available_quantity: int
    reserved_quantity: int
    damaged_quantity: int
    reorder_level: int

    model_config = ConfigDict(
        from_attributes=True
    )