from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity: str
    entity_id: int | None
    details: dict[str, Any] | None
    ip_address: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)