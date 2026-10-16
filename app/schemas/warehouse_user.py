
from pydantic import BaseModel, Field


class WarehouseUserCreate(BaseModel):
    user_id: int = Field(gt=0)
