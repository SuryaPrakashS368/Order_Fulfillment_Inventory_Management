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


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name = Column(
        String(100),
        nullable=False
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash = Column(
        String(255),
        nullable=False
    )
    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        nullable=False,
        index=True
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    last_login_at = Column(
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
    role = relationship(
        "Role",
        back_populates="users"
    )
    warehouse_assignments = relationship(
        "WarehouseUser",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    orders = relationship(
        "Order",
        foreign_keys="Order.customer_id",
        back_populates="customer"
    )
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )
    inventory_transactions = relationship(
        "InventoryTransaction",
        back_populates="user"
    )
    order_assignments = relationship(
        "OrderAssignment",
        foreign_keys="OrderAssignment.agent_id",
        back_populates="agent"
    )
    assignments_created = relationship(
        "OrderAssignment",
        foreign_keys="OrderAssignment.assigned_by",
        back_populates="assigned_by_user"
    )
    order_status_changes = relationship(
        "OrderStatusHistory",
        foreign_keys="OrderStatusHistory.changed_by",
        back_populates="changed_by_user"
    )
    returns = relationship(
        "Return",
        foreign_keys="Return.customer_id",
        back_populates="customer"
    )
    idempotency_keys = relationship(
        "IdempotencyKey",
        back_populates="user",
        cascade="all, delete-orphan"
    )