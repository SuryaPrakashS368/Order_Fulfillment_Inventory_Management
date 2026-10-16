
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class PaymentConfirmRequest(BaseModel):
    order_id: int = Field(gt=0)

    payment_method: Literal[
        "UPI",
        "CARD",
        "NET_BANKING",
        "CASH",
    ]


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    customer_id: int
    amount: Decimal
    payment_method: str
    payment_status: str
    idempotency_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
