from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Boolean,
    CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReturnItem(Base):
    __tablename__ = "return_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_return_item_quantity_positive"
        ),
        UniqueConstraint(
            "return_id",
            "order_item_id",
            name="uq_return_item_order_item"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    return_id = Column(
        Integer,
        ForeignKey("returns.id"),
        nullable=False,
        index=True
    )
    order_item_id = Column(
        Integer,
        ForeignKey("order_items.id"),
        nullable=False,
        index=True
    )
    quantity = Column(
        Integer,
        nullable=False
    )
    restocked = Column(
        Boolean,
        default=False,
        nullable=False
    )
    return_record = relationship(
        "Return",
        back_populates="items"
    )
    order_item = relationship(
        "OrderItem"
    )