from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    reference_entity: str | None
    reference_id: int | None
    is_read: bool
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


class UnreadNotificationCountResponse(BaseModel):
    unread_count: int


class NotificationMessageResponse(BaseModel):
    message: str
    updated_count: int