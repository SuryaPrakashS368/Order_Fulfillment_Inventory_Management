from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import OrderStatus
from app.models.order_status_history import OrderStatusHistory

from app.repositories.order_repository import (
    get_order_by_id
)

from app.repositories.order_status_history_repository import (
    create_status_history
)

from app.services.inventory_transaction_service import (
    release_inventory_service
)


CANCELLABLE_STATUSES = {
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED
}


def cancel_order_service(
    db: Session,
    order_id: int,
    user_id: int,
    reason: str
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status not in CANCELLABLE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Order cannot be cancelled "
                f"when its status is {order.status.value}"
            )
        )

    previous_status = order.status

    try:
        # Release every order item's reserved stock.
        for item in order.items:
            release_inventory_service(
                db=db,
                product_id=item.product_id,
                warehouse_id=order.warehouse_id,
                quantity=item.quantity,
                order_id=order.id,
                user_id=user_id
            )

        # Update the order only after all releases succeed.
        order.status = OrderStatus.CANCELLED

        history = OrderStatusHistory(
            order_id=order.id,
            from_status=previous_status,
            to_status=OrderStatus.CANCELLED,
            changed_by=user_id,
            reason=reason
        )

        create_status_history(db, history)

        db.flush()
        db.commit()
        db.refresh(order)

        return {
            "message": "Order cancelled successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status.value
        }

    except Exception:
        db.rollback()
        raise