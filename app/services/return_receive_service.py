from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles

from app.models.order import OrderStatus
from app.models.return_model import ReturnStatus
from app.models.inventory_transaction import (
    InventoryTransaction,
    InventoryTransactionType
)

from app.repositories.return_repository import (
    get_return_by_id
)

from app.repositories.inventory_repository import (
    get_inventory_by_product_and_warehouse
)

from app.repositories.inventory_transaction_repository import (
    create_transaction
)

from app.repositories.warehouse_user_repository import (
    get_assignment as get_warehouse_assignment
)


def receive_return_service(
    db: Session,
    return_id: int,
    receiver_id: int,
    receiver_role: str
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

    if receiver_role not in {
        Roles.ADMIN,
        Roles.WAREHOUSE_MANAGER,
        Roles.FULFILLMENT_AGENT
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot receive returned inventory"
        )

    order = return_record.order

    if receiver_role != Roles.ADMIN:
        warehouse_assignment = get_warehouse_assignment(
            db,
            order.warehouse_id,
            receiver_id
        )

        if not warehouse_assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this warehouse"
            )

    if return_record.status != ReturnStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only approved returns can be received"
        )

    try:
        # Lock and update inventory records in the transaction.
        for return_item in return_record.items:
            order_item = return_item.order_item

            inventory = (
                get_inventory_by_product_and_warehouse(
                    db,
                    order_item.product_id,
                    order.warehouse_id
                )
            )

            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Inventory not found for product "
                        f"{order_item.product_id}"
                    )
                )

            if return_item.restocked:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This item has already been restocked"
                )

            inventory.available_quantity += return_item.quantity

            transaction = InventoryTransaction(
                product_id=order_item.product_id,
                warehouse_id=order.warehouse_id,
                transaction_type=InventoryTransactionType.RETURN,
                quantity=return_item.quantity,
                reference_entity="Return",
                reference_id=return_record.id,
                user_id=receiver_id,
                transaction_metadata={
                    "order_id": order.id,
                    "return_item_id": return_item.id,
                    "return_reason": return_record.reason
                }
            )

            create_transaction(db, transaction)
            return_item.restocked = True

        return_record.status = ReturnStatus.RECEIVED
        return_record.received_by = receiver_id

        # Mark the order RETURNED only if all quantities in the
        # order have been received back through completed returns.
        from app.models.return_item import ReturnItem
        from app.models.return_model import Return

        for order_item in order.items:
            received_quantity = (
                db.query(ReturnItem)
                .join(
                    Return,
                    ReturnItem.return_id == Return.id
                )
                .filter(
                    ReturnItem.order_item_id == order_item.id,
                    Return.status.in_([
                        ReturnStatus.RECEIVED,
                        ReturnStatus.REFUNDED
                    ])
                )
                .with_for_update()
                .all()
            )

            total_received = sum(
                item.quantity
                for item in received_quantity
            )

            if total_received < order_item.quantity:
                break
        else:
            order.status = OrderStatus.RETURNED

        db.flush()
        db.commit()
        db.refresh(return_record)

        return return_record

    except Exception:
        db.rollback()
        raise


def refund_return_service(
    db: Session,
    return_id: int,
    reviewer_role: str
):
    from app.models.order import PaymentStatus
    from app.repositories.return_repository import (
        get_return_by_id
    )

    if reviewer_role != Roles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an Admin can mark a refund as processed"
        )

    return_record = get_return_by_id(
        db,
        return_id
    )

    if not return_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    if return_record.status != ReturnStatus.RECEIVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only received returns can be refunded"
        )

    try:
        return_record.status = ReturnStatus.REFUNDED

        # Only mark the whole order refunded if this return covers
        # the full order value. A real gateway refund is separate.
        if Decimal(str(return_record.refund_amount)) >= Decimal(
            str(return_record.order.total_amount)
        ):
            return_record.order.payment_status = (
                PaymentStatus.REFUNDED
            )

        db.commit()
        db.refresh(return_record)

        return return_record

    except Exception:
        db.rollback()
        raise