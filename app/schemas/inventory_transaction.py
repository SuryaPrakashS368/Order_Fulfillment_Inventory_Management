from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

from app.models.inventory_transaction import (
    InventoryTransactionType
)


class InventoryAdjustmentRequest(BaseModel):

    product_id: int = Field(
        gt=0
    )
    warehouse_id: int = Field(
        gt=0
    )
    quantity: int
    reason: str = Field(
        min_length=3,
        max_length=500
    )


class InventoryPurchaseRequest(BaseModel):

    product_id: int = Field(
        gt=0
    )
    warehouse_id: int = Field(
        gt=0
    )
    quantity: int = Field(
        gt=0
    )
    reason: str | None = Field(
        default=None,
        max_length=500
    )


class InventoryDamageRequest(BaseModel):

    product_id: int = Field(
        gt=0
    )
    warehouse_id: int = Field(
        gt=0
    )
    quantity: int = Field(
        gt=0
    )
    reason: str = Field(
        min_length=3,
        max_length=500
    )


class InventoryTransactionResponse(BaseModel):

    id: int
    product_id: int
    warehouse_id: int
    transaction_type: InventoryTransactionType
    quantity: int
    reference_entity: str | None
    reference_id: int | None
    user_id: int | None
    transaction_metadata: dict | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )