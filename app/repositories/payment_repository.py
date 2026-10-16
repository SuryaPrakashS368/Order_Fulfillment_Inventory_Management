
from sqlalchemy.orm import Session

from app.models.payment import Payment


def get_payment_by_idempotency_key(
    db: Session,
    idempotency_key: str,
):
    return (
        db.query(Payment)
        .filter(
            Payment.idempotency_key == idempotency_key
        )
        .first()
    )


def get_successful_payment_for_order(
    db: Session,
    order_id: int,
):
    return (
        db.query(Payment)
        .filter(
            Payment.order_id == order_id,
            Payment.payment_status == "PAID",
        )
        .first()
    )


def get_payment_by_id(
    db: Session,
    payment_id: int,
):
    return (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )


def create_payment(
    db: Session,
    payment: Payment,
):
    db.add(payment)
    db.flush()
    return payment
