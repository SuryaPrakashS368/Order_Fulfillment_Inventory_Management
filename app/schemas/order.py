from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

from app.models.order import (
    OrderStatus,
    PaymentStatus
)


class OrderItemCreate(BaseModel):

    product_id: int = Field(
        gt=0
    )
    quantity: int = Field(
        gt=0
    )


class OrderCreate(BaseModel):

    warehouse_id: int = Field(
        gt=0
    )
    items: list[OrderItemCreate] = Field(
        min_length=1,
        max_length=100
    )

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    reason: str | None = Field(
        default=None,
        max_length=500
    )    
    
class OrderCancellationRequest(BaseModel):
    reason: str = Field(
        min_length=3,
        max_length=500
    )


class OrderCancellationResponse(BaseModel):
    message: str
    order_id: int
    order_number: str
    status: str

class OrderStatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    from_status: OrderStatus | None
    to_status: OrderStatus
    changed_by: int
    reason: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class OrderItemResponse(BaseModel):

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderResponse(BaseModel):

    id: int
    order_number: str
    customer_id: int
    warehouse_id: int
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    expected_delivery_date: datetime | None
    created_at: datetime
    updated_at: datetime

    items: list[OrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )