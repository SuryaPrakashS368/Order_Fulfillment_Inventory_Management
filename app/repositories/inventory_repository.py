from sqlalchemy.orm import Session

from app.models.inventory import Inventory


def get_inventory_by_id(
    db: Session,
    inventory_id: int
):
    return (
        db.query(Inventory)
        .filter(
            Inventory.id == inventory_id
        )
        .first()
    )


def get_inventory_by_product_and_warehouse(
    db: Session,
    product_id: int,
    warehouse_id: int
):
    return (
        db.query(Inventory)
        .filter(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id
        )
        .first()
    )


def get_inventory(
    db: Session,
    product_id: int | None = None,
    warehouse_id: int | None = None
):
    query = db.query(Inventory)

    if product_id is not None:

        query = query.filter(
            Inventory.product_id == product_id
        )

    if warehouse_id is not None:

        query = query.filter(
            Inventory.warehouse_id == warehouse_id
        )

    return (
        query
        .order_by(Inventory.id.desc())
        .all()
    )


def get_inventory_by_warehouse(
    db: Session,
    warehouse_id: int
):
    return (
        db.query(Inventory)
        .filter(
            Inventory.warehouse_id == warehouse_id
        )
        .order_by(Inventory.id.desc())
        .all()
    )


def get_inventory_by_product(
    db: Session,
    product_id: int
):
    return (
        db.query(Inventory)
        .filter(
            Inventory.product_id == product_id
        )
        .order_by(Inventory.id.desc())
        .all()
    )


def create_inventory(
    db: Session,
    inventory: Inventory
):
    db.add(inventory)

    db.commit()

    db.refresh(inventory)

    return inventory


def update_inventory(
    db: Session,
    inventory: Inventory
):
    db.commit()

    db.refresh(inventory)

    return inventory


def get_inventory_for_update(
db: Session,
product_id: int,
warehouse_id: int,
):


    return (
    db.query(Inventory)
    .filter(
        Inventory.product_id == product_id,
        Inventory.warehouse_id == warehouse_id,
    )
    .with_for_update()
    .first()
)