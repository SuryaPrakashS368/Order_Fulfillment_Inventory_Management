from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.warehouse_user import WarehouseUser
from app.models.order_assignment import OrderAssignment


def get_total_orders(
    db: Session,
    warehouse_ids: list[int] | None = None,
):
    query = db.query(func.count(Order.id))

    if warehouse_ids is not None:
        query = query.filter(
            Order.warehouse_id.in_(warehouse_ids)
        )

    return query.scalar() or 0


def get_orders_by_status(
    db: Session,
    warehouse_ids: list[int] | None = None,
):
    query = db.query(
        Order.status,
        func.count(Order.id)
    )

    if warehouse_ids is not None:
        query = query.filter(
            Order.warehouse_id.in_(warehouse_ids)
        )

    rows = query.group_by(Order.status).all()

    return {
        (
            status.value
            if hasattr(status, "value")
            else str(status)
        ): count
        for status, count in rows
    }


def get_total_products(db: Session):
    return db.query(
        func.count(Product.id)
    ).scalar() or 0


def get_inventory_summary(
    db: Session,
    warehouse_ids: list[int] | None = None,
):
    query = db.query(
        func.coalesce(
            func.sum(Inventory.available_quantity), 0
        ),
        func.coalesce(
            func.sum(Inventory.reserved_quantity), 0
        ),
        func.coalesce(
            func.sum(Inventory.damaged_quantity), 0
        ),
    )

    if warehouse_ids is not None:
        query = query.filter(
            Inventory.warehouse_id.in_(warehouse_ids)
        )

    available, reserved, damaged = query.one()

    return {
        "available_quantity": int(available),
        "reserved_quantity": int(reserved),
        "damaged_quantity": int(damaged),
    }


def get_low_stock_inventory(
    db: Session,
    warehouse_ids: list[int] | None = None,
    skip: int = 0,
    limit: int = 20,
):
    query = (
        db.query(Inventory)
        .filter(
            Inventory.available_quantity
            <= Inventory.reorder_level
        )
    )

    if warehouse_ids is not None:
        query = query.filter(
            Inventory.warehouse_id.in_(warehouse_ids)
        )

    return (
        query
        .order_by(
            Inventory.available_quantity.asc(),
            Inventory.id.asc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_warehouse_ids(
    db: Session,
    user_id: int,
):
    rows = (
        db.query(WarehouseUser.warehouse_id)
        .filter(WarehouseUser.user_id == user_id)
        .all()
    )

    return [row[0] for row in rows]


def get_agent_assignment_summary(
    db: Session,
    agent_id: int,
):
    return (
        db.query(func.count(OrderAssignment.id))
        .join(
            Order,
            Order.id == OrderAssignment.order_id
        )
        .filter(
            OrderAssignment.agent_id == agent_id,
            Order.status.in_([
                OrderStatus.CONFIRMED,
                OrderStatus.PROCESSING,
                OrderStatus.PACKED,
                OrderStatus.SHIPPED,
            ])
        )
        .scalar()
        or 0
    )