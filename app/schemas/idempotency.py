from pydantic import BaseModel, ConfigDict


class IdempotencyKeyResponse(BaseModel):
    id: int
    key: str
    user_id: int
    resource_type: str
    resource_id: int

    model_config = ConfigDict(from_attributes=True)