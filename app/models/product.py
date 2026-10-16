from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    CheckConstraint
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class Product(Base):

    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="ck_product_price_non_negative"
        ),
        CheckConstraint(
            "cost_price >= 0",
            name="ck_product_cost_price_non_negative"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    sku = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    name = Column(
        String(200),
        nullable=False,
        index=True
    )
    description = Column(
        Text,
        nullable=True
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
        index=True
    )
    price = Column(
        Numeric(12, 2),
        nullable=False
    )
    cost_price = Column(
        Numeric(12, 2),
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
    category = relationship(
        "Category",
        back_populates="products"
    )
    inventory = relationship(
        "Inventory",
        back_populates="product"
    )
    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )
    inventory_transactions = relationship(
        "InventoryTransaction",
        back_populates="product"
    )