
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order, PaymentStatus
from app.models.payment import Payment

from app.repositories.payment_repository import (
    create_payment,
    get_payment_by_idempotency_key,
    get_successful_payment_for_order,
)


def confirm_payment_service(
    db: Session,
    order_id: int,
    customer_id: int,
    payment_method: str,
    idempotency_key: str,
    is_admin: bool = False,
):
    try:
        # Lock the order while processing payment confirmation.
        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .with_for_update()
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        if not is_admin and order.customer_id != customer_id:
            raise HTTPException(
                status_code=403,
                detail="You cannot pay for another customer's order",
            )

        # An identical idempotency key must not create another payment.
        existing = get_payment_by_idempotency_key(
            db,
            idempotency_key,
        )

        if existing:
            if (
                existing.order_id != order_id
                or existing.customer_id != customer_id
                or existing.payment_method != payment_method
            ):
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Idempotency key was already used "
                        "for a different payment request"
                    ),
                )

            return existing

        # Never simulate a second successful payment for the same order.
        successful_payment = get_successful_payment_for_order(
            db,
            order_id,
        )

        if successful_payment:
            raise HTTPException(
                status_code=409,
                detail="This order has already been paid",
            )

        if order.payment_status == PaymentStatus.REFUNDED:
            raise HTTPException(
                status_code=409,
                detail="A refunded order cannot be paid again",
            )

        payment = Payment(
            order_id=order.id,
            customer_id=order.customer_id,
            amount=order.total_amount,
            payment_method=payment_method,
            payment_status="PAID",
            idempotency_key=idempotency_key,
        )

        create_payment(db, payment)

        # Keep the existing order payment status in sync.
        order.payment_status = PaymentStatus.PAID

        db.commit()
        db.refresh(payment)

        return payment

    except Exception:
        db.rollback()
        raise
