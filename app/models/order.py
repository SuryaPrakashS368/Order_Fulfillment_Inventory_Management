from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Enum as SQLEnum,
    CheckConstraint
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderStatus(str, enum.Enum):

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    RETURNED = "RETURNED"


class PaymentStatus(str, enum.Enum):

    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Order(Base):

    __tablename__ = "orders"

    __table_args__ = (

        CheckConstraint(
            "total_amount >= 0",
            name="ck_order_total_amount_non_negative"
        ),

    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    order_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )
    total_amount = Column(
        Numeric(12, 2),
        nullable=False
    )
    status = Column(
        SQLEnum(
            OrderStatus,
            name="order_status"
        ),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True
    )
    payment_status = Column(
        SQLEnum(
            PaymentStatus,
            name="payment_status"
        ),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True
    )
    expected_delivery_date = Column(
        DateTime,
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
    customer = relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="orders"
    )
    warehouse = relationship(
        "Warehouse",
        back_populates="orders"
    )
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    status_history = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    assignments = relationship(
        "OrderAssignment",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    returns = relationship(
        "Return",
        back_populates="order"
    )