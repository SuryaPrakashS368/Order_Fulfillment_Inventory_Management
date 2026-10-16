from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

from app.models.return_model import ReturnStatus


class ReturnItemCreate(BaseModel):
    order_item_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class ReturnCreate(BaseModel):
    order_id: int = Field(gt=0)
    reason: str = Field(
        min_length=3,
        max_length=1000
    )
    items: list[ReturnItemCreate] = Field(
        min_length=1,
        max_length=100
    )


class ReturnReviewRequest(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=1000
    )


class ReturnResponse(BaseModel):
    id: int
    order_id: int
    customer_id: int
    status: ReturnStatus
    reason: str
    refund_amount: Decimal
    reviewed_by: int | None
    received_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ReturnItemResponse(BaseModel):
    id: int
    return_id: int
    order_item_id: int
    quantity: int
    restocked: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class ReturnDetailResponse(ReturnResponse):
    items: list[ReturnItemResponse]