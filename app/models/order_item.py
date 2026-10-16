from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    ForeignKey,
    Numeric
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderItem(Base):

    __tablename__ = "order_items"

    __table_args__ = (

        CheckConstraint(
            "quantity > 0",
            name="ck_order_item_quantity_positive"
        ),

        CheckConstraint(
            "unit_price >= 0",
            name="ck_order_item_unit_price_non_negative"
        ),

        CheckConstraint(
            "discount >= 0",
            name="ck_order_item_discount_non_negative"
        ),

        CheckConstraint(
            "tax >= 0",
            name="ck_order_item_tax_non_negative"
        ),

        CheckConstraint(
            "total >= 0",
            name="ck_order_item_total_non_negative"
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
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )
    quantity = Column(
        Integer,
        nullable=False
    )
    unit_price = Column(
        Numeric(12, 2),
        nullable=False
    )
    discount = Column(
        Numeric(12, 2),
        default=0,
        nullable=False
    )
    tax = Column(
        Numeric(12, 2),
        default=0,
        nullable=False
    )
    total = Column(
        Numeric(12, 2),
        nullable=False
    )
    order = relationship(
        "Order",
        back_populates="items"
    )
    product = relationship(
        "Product",
        back_populates="order_items"
    )