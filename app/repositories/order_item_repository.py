from sqlalchemy.orm import Session

from app.models.order_item import OrderItem


def create_order_item(
    db: Session,
    order_item: OrderItem
):

    db.add(order_item)

    db.flush()

    return order_item


def get_order_items(
    db: Session,
    order_id: int
):

    return (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == order_id
        )
        .order_by(
            OrderItem.id
        )
        .all()
    )