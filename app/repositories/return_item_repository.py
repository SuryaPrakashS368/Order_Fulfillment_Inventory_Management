from sqlalchemy.orm import Session

from app.models.return_item import ReturnItem


def get_return_item_by_id(
    db: Session,
    return_item_id: int
):
    return (
        db.query(ReturnItem)
        .filter(ReturnItem.id == return_item_id)
        .first()
    )


def get_return_items_for_order_item(
    db: Session,
    order_item_id: int
):
    return (
        db.query(ReturnItem)
        .filter(
            ReturnItem.order_item_id == order_item_id
        )
        .all()
    )