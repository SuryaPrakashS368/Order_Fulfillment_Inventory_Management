from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum
)

from sqlalchemy.orm import relationship

from app.core.database import Base

from app.models.order import OrderStatus


class OrderStatusHistory(Base):

    __tablename__ = "order_status_history"

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
    from_status = Column(
        SQLEnum(
            OrderStatus,
            name="order_history_from_status"
        ),
        nullable=True
    )
    to_status = Column(
        SQLEnum(
            OrderStatus,
            name="order_history_to_status"
        ),
        nullable=False
    )
    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    reason = Column(
        Text,
        nullable=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    order = relationship(
        "Order",
        back_populates="status_history"
    )
    changed_by_user = relationship(
        "User",
        foreign_keys=[changed_by],
        back_populates="order_status_changes"
    )