from sqlalchemy.orm import Session

from app.models.order import Order


def get_order_by_id(
    db: Session,
    order_id: int
):

    return (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )


def get_order_by_number(
    db: Session,
    order_number: str
):

    return (
        db.query(Order)
        .filter(
            Order.order_number == order_number
        )
        .first()
    )


def get_customer_orders(
    db: Session,
    customer_id: int,
    skip: int = 0,
    limit: int = 20,
    status=None,
    order_number: str | None = None,
):

    query = db.query(Order).filter(
        Order.customer_id == customer_id
    )

    # Filter by order status
    if status is not None:
        query = query.filter(
            Order.status == status
        )

    # Search by order number
    if order_number:
        query = query.filter(
            Order.order_number.ilike(
                f"%{order_number.strip()}%"
            )
        )

    # Newest orders first, with a stable tie-breaker
    return (
        query
        .order_by(
            Order.created_at.desc(),
            Order.id.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_order(
    db: Session,
    order: Order
):

    db.add(order)

    db.flush()

    return order