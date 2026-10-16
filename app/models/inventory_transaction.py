from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class InventoryTransactionType(str, enum.Enum):

    PURCHASE = "PURCHASE"
    SALE = "SALE"
    RESERVATION = "RESERVATION"
    RELEASE = "RELEASE"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    RETURN = "RETURN"
    DAMAGE = "DAMAGE"


class InventoryTransaction(Base):

    __tablename__ = "inventory_transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )
    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )
    transaction_type = Column(
        SQLEnum(
            InventoryTransactionType,
            name="inventory_transaction_type"
        ),
        nullable=False,
        index=True
    )
    quantity = Column(
        Integer,
        nullable=False
    )
    reference_entity = Column(
        String(100),
        nullable=True
    )
    reference_id = Column(
        Integer,
        nullable=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )
    transaction_metadata = Column(
        JSON,
        nullable=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    product = relationship(
        "Product",
        back_populates="inventory_transactions"
    )
    warehouse = relationship(
        "Warehouse",
        back_populates="inventory_transactions"
    )
    user = relationship(
        "User",
        back_populates="inventory_transactions"
    )