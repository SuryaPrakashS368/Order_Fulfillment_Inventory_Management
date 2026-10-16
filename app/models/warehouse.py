from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    CheckConstraint
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class Warehouse(Base):

    __tablename__ = "warehouses"

    __table_args__ = (
        CheckConstraint(
            "capacity > 0",
            name="ck_warehouse_capacity_positive"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name = Column(
        String(150),
        nullable=False,
        index=True
    )
    location = Column(
        String(255),
        nullable=False
    )
    capacity = Column(
        Integer,
        nullable=False
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
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
    users = relationship(
        "WarehouseUser",
        back_populates="warehouse",
        cascade="all, delete-orphan"
    )
    inventory = relationship(
        "Inventory",
        back_populates="warehouse"
    )
    orders = relationship(
        "Order",
        back_populates="warehouse"
    )
    inventory_transactions = relationship(
        "InventoryTransaction",
        back_populates="warehouse"
    )