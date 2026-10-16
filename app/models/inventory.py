from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class Inventory(Base):

    __tablename__ = "inventory"

    __table_args__ = (

        UniqueConstraint(
            "product_id",
            "warehouse_id",
            name="uq_inventory_product_warehouse"
        ),

        CheckConstraint(
            "available_quantity >= 0",
            name="ck_inventory_available_non_negative"
        ),

        CheckConstraint(
            "reserved_quantity >= 0",
            name="ck_inventory_reserved_non_negative"
        ),

        CheckConstraint(
            "damaged_quantity >= 0",
            name="ck_inventory_damaged_non_negative"
        ),

        CheckConstraint(
            "reorder_level >= 0",
            name="ck_inventory_reorder_non_negative"
        ),
    )

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
    available_quantity = Column(
        Integer,
        default=0,
        nullable=False
    )
    reserved_quantity = Column(
        Integer,
        default=0,
        nullable=False
    )
    damaged_quantity = Column(
        Integer,
        default=0,
        nullable=False
    )
    reorder_level = Column(
        Integer,
        default=0,
        nullable=False
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
    product = relationship(
        "Product",
        back_populates="inventory"
    )
    warehouse = relationship(
        "Warehouse",
        back_populates="inventory"
    )