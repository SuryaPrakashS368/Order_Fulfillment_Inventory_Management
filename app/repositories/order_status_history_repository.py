from sqlalchemy.orm import Session

from app.models.order_status_history import OrderStatusHistory


def create_status_history(
    db: Session,
    history: OrderStatusHistory
):
    db.add(history)
    db.flush()

    return history


def get_order_status_history(
    db: Session,
    order_id: int
):
    return (
        db.query(OrderStatusHistory)
        .filter(
            OrderStatusHistory.order_id == order_id
        )
        .order_by(
            OrderStatusHistory.id.asc()
        )
        .all()
    )