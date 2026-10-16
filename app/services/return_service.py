from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles

from app.models.order import OrderStatus
from app.models.return_model import Return, ReturnStatus
from app.models.return_item import ReturnItem

from app.repositories.order_repository import (
    get_order_by_id
)

from app.repositories.return_repository import (
    get_return_by_id,
    get_returns_by_customer,
    get_all_returns,
    get_returns_by_order,
    create_return,
    create_return_item
)

from app.repositories.return_item_repository import (
    get_return_items_for_order_item
)


ACTIVE_RETURN_STATUSES = {
    ReturnStatus.REQUESTED,
    ReturnStatus.APPROVED,
    ReturnStatus.RECEIVED,
    ReturnStatus.REFUNDED
}


def create_return_service(
    db: Session,
    order_id: int,
    customer_id: int,
    reason: str,
    items
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot return another customer's order"
        )

    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only delivered orders can be returned"
        )

    if order.payment_status != "PAID" and getattr(
        order.payment_status, "value", order.payment_status
    ) != "PAID":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only paid orders can be returned"
        )

    # Reject repeated order-item IDs in one request.
    requested_ids = [item.order_item_id for item in items]

    if len(requested_ids) != len(set(requested_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Each order item must appear only once"
        )

    order_items_by_id = {
        item.id: item
        for item in order.items
    }

    validated_items = []
    refund_amount = Decimal("0.00")

    for request_item in items:
        order_item = order_items_by_id.get(
            request_item.order_item_id
        )

        if not order_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Order item {request_item.order_item_id} "
                    "does not belong to this order"
                )
            )

        previous_return_items = (
            get_return_items_for_order_item(
                db,
                order_item.id
            )
        )

        already_requested = sum(
            previous_item.quantity
            for previous_item in previous_return_items
            if previous_item.return_record.status
            in ACTIVE_RETURN_STATUSES
        )

        remaining_quantity = (
            order_item.quantity - already_requested
        )

        if request_item.quantity > remaining_quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Return quantity exceeds the remaining "
                    f"quantity for order item {order_item.id}"
                )
            )

        # Use the saved order-line total rather than today's
        # product price. This preserves the original price.
        line_total = Decimal(str(order_item.total))
        per_unit_value = (
            line_total / Decimal(order_item.quantity)
        )

        refund_amount += (
            per_unit_value * request_item.quantity
        )

        validated_items.append(
            (order_item, request_item.quantity)
        )

    try:
        return_record = Return(
            order_id=order.id,
            customer_id=customer_id,
            status=ReturnStatus.REQUESTED,
            reason=reason,
            refund_amount=refund_amount.quantize(
                Decimal("0.01")
            )
        )

        create_return(db, return_record)

        for order_item, quantity in validated_items:
            create_return_item(
                db,
                ReturnItem(
                    return_id=return_record.id,
                    order_item_id=order_item.id,
                    quantity=quantity
                )
            )

        db.commit()
        db.refresh(return_record)

        return return_record

    except Exception:
        db.rollback()
        raise


def get_customer_returns_service(
    db: Session,
    customer_id: int
):
    return get_returns_by_customer(
        db,
        customer_id
    )


def get_all_returns_service(
    db: Session
):
    return get_all_returns(db)


def get_return_service(
    db: Session,
    return_id: int
):
    return_record = get_return_by_id(
        db,
        return_id
    )

    if not return_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    return return_record