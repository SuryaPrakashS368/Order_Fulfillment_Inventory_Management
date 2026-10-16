from sqlalchemy.orm import Session

from app.models.return_model import Return
from app.models.return_item import ReturnItem


def get_return_by_id(
    db: Session,
    return_id: int
):
    return (
        db.query(Return)
        .filter(Return.id == return_id)
        .first()
    )


def get_returns_by_order(
    db: Session,
    order_id: int
):
    return (
        db.query(Return)
        .filter(Return.order_id == order_id)
        .order_by(Return.id.desc())
        .all()
    )


def get_returns_by_customer(
    db: Session,
    customer_id: int
):
    return (
        db.query(Return)
        .filter(Return.customer_id == customer_id)
        .order_by(Return.id.desc())
        .all()
    )


def get_all_returns(
    db: Session
):
    return (
        db.query(Return)
        .order_by(Return.id.desc())
        .all()
    )


def create_return(
    db: Session,
    return_record: Return
):
    db.add(return_record)
    db.flush()

    return return_record


def create_return_item(
    db: Session,
    return_item: ReturnItem
):
    db.add(return_item)
    db.flush()

    return return_item


def get_return_items(
    db: Session,
    return_id: int
):
    return (
        db.query(ReturnItem)
        .filter(ReturnItem.return_id == return_id)
        .all()
    )