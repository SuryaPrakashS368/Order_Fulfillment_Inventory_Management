from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class RolePermission(Base):

    __tablename__ = "role_permissions"

    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permission"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        nullable=False,
        index=True
    )
    permission_id = Column(
        Integer,
        ForeignKey("permissions.id"),
        nullable=False,
        index=True
    )
    role = relationship(
        "Role",
        back_populates="role_permissions"
    )
    permission = relationship(
        "Permission",
        back_populates="role_permissions"
    )