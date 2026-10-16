from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.database import get_db

from app.dependencies.auth import get_current_user

from app.repositories.order_repository import (
    get_order_by_id
)

from app.repositories.warehouse_user_repository import (
    get_assignment
)


def check_order_warehouse_access(
    db: Session,
    order,
    current_user
):
    # Admin can access every warehouse.
    if current_user.role.name == Roles.ADMIN:
        return

    assignment = get_assignment(
        db,
        order.warehouse_id,
        current_user.id
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not assigned to "
                "this order's warehouse"
            )
        )


def get_accessible_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = get_order_by_id(
        db,
        order_id
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Customer can access only their own order.
    if current_user.role.name == Roles.CUSTOMER:
        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access this order"
            )

        return order

    check_order_warehouse_access(
        db,
        order,
        current_user
    )

    return order