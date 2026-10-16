from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "key",
            name="uq_idempotency_user_key",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    resource_type = Column(
        String(100),
        nullable=False,
    )
    resource_id = Column(
        Integer,
        nullable=True,
    )
    request_hash = Column(
        String(64),
        nullable=False,
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    user = relationship(
        "User",
        back_populates="idempotency_keys",
    )