from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderAssignmentCreate(BaseModel):
    agent_id: int = Field(gt=0)


class OrderAssignmentResponse(BaseModel):
    id: int
    order_id: int
    agent_id: int
    assigned_by: int
    assigned_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )