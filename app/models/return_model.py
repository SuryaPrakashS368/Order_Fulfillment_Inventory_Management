from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    Enum as SQLEnum,
    CheckConstraint
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReturnStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RECEIVED = "RECEIVED"
    REFUNDED = "REFUNDED"


class Return(Base):
    __tablename__ = "returns"

    __table_args__ = (
        CheckConstraint(
            "refund_amount >= 0",
            name="ck_return_refund_amount_non_negative"
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
    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    status = Column(
        SQLEnum(ReturnStatus, name="return_status"),
        default=ReturnStatus.REQUESTED,
        nullable=False,
        index=True
    )
    reason = Column(
        Text,
        nullable=False
    )
    refund_amount = Column(
        Numeric(12, 2),
        default=0,
        nullable=False
    )
    reviewed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    received_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    order = relationship(
        "Order",
        back_populates="returns"
    )
    customer = relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="returns"
    )
    items = relationship(
        "ReturnItem",
        back_populates="return_record",
        cascade="all, delete-orphan"
    )
    reviewer = relationship(
        "User",
        foreign_keys=[reviewed_by]
    )
    receiver = relationship(
        "User",
        foreign_keys=[received_by]
    )