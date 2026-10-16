from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderAssignment(Base):
    __tablename__ = "order_assignments"

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "agent_id",
            name="uq_order_assignment_order_agent"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )
    agent_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    assigned_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    assigned_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    order = relationship(
        "Order",
        back_populates="assignments"
    )
    agent = relationship(
        "User",
        foreign_keys=[agent_id],
        back_populates="order_assignments"
    )
    assigned_by_user = relationship(
        "User",
        foreign_keys=[assigned_by],
        back_populates="assignments_created"
    )