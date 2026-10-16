from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    __table_args__ = (
        Index(
            "ix_audit_entity_created",
            "entity",
            "entity_id",
            "created_at",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    action = Column(
        String(100),
        nullable=False,
        index=True,
    )
    entity = Column(
        String(100),
        nullable=False,
        index=True,
    )
    entity_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    details = Column(JSON, nullable=True)
    ip_address = Column(
        String(45),
        nullable=True,
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    user = relationship(
        "User",
        back_populates="audit_logs",
    )
