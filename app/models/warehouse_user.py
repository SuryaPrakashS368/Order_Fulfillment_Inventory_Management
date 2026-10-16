from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class WarehouseUser(Base):

    __tablename__ = "warehouse_users"

    __table_args__ = (
        UniqueConstraint(
            "warehouse_id",
            "user_id",
            name="uq_warehouse_user"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    warehouse = relationship(
        "Warehouse",
        back_populates="users"
    )
    user = relationship(
        "User",
        back_populates="warehouse_assignments"
    )