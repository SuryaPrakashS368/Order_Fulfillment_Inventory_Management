from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    __table_args__ = (
        Index(
            "ix_notifications_user_read_created",
            "user_id",
            "is_read",
            "created_at"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    title = Column(
        String(200),
        nullable=False
    )
    message = Column(
        Text,
        nullable=False
    )
    notification_type = Column(
        String(100),
        nullable=False,
        index=True
    )
    reference_entity = Column(
        String(100),
        nullable=True
    )
    reference_id = Column(
        Integer,
        nullable=True
    )
    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    read_at = Column(
        DateTime,
        nullable=True
    )
    user = relationship(
        "User",
        back_populates="notifications"
    )