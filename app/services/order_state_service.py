from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import (
    ORDER_TRANSITIONS,
    ROLE_STATUS_TRANSITIONS,
    Roles
)

from app.models.order import OrderStatus
from app.models.order_status_history import OrderStatusHistory

from app.repositories.order_repository import (
    get_order_by_id
)

from app.repositories.order_status_history_repository import (
    create_status_history,
    get_order_status_history
)


def validate_status_transition(
    current_status: OrderStatus,
    new_status: OrderStatus
):
    current_value = current_status.value
    new_value = new_status.value

    allowed_statuses = ORDER_TRANSITIONS.get(
        current_value,
        []
    )

    if new_value not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid order status transition: "
                f"{current_value} -> {new_value}"
            )
        )


def validate_role_transition(
    role_name: str,
    current_status: OrderStatus,
    new_status: OrderStatus
):
    transition = (
        current_status.value,
        new_status.value
    )

    allowed_transitions = ROLE_STATUS_TRANSITIONS.get(
        role_name,
        set()
    )

    if transition not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Role '{role_name}' is not allowed "
                f"to change order status from "
                f"{current_status.value} to "
                f"{new_status.value}"
            )
        )


def update_order_status_service(
    db: Session,
    order_id: int,
    new_status: OrderStatus,
    changed_by: int,
    role_name: str,
    reason: str | None = None
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

    current_status = order.status

    if current_status == new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Order is already in "
                f"{current_status.value} status"
            )
        )

    # Validate state-machine transition
    validate_status_transition(
        current_status,
        new_status
    )

    # Validate role permission
    validate_role_transition(
        role_name,
        current_status,
        new_status
    )

    try:
        order.status = new_status

        history = OrderStatusHistory(
            order_id=order.id,
            from_status=current_status,
            to_status=new_status,
            changed_by=changed_by,
            reason=reason
        )

        create_status_history(
            db,
            history
        )

        db.flush()
        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def get_order_status_history_service(
    db: Session,
    order_id: int
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

    return get_order_status_history(
        db,
        order_id
    )