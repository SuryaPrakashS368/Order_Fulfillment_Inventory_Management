from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

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
    token_hash = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    expires_at = Column(
        DateTime,
        nullable=False
    )
    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    revoked_at = Column(
        DateTime,
        nullable=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    user = relationship(
        "User",
        back_populates="refresh_tokens"
    )