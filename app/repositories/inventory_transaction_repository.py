from sqlalchemy.orm import Session

from app.models.inventory_transaction import (
    InventoryTransaction
)


def create_transaction(
    db: Session,
    transaction: InventoryTransaction
):

    db.add(transaction)

    db.flush()

    return transaction


def get_transaction_by_id(
    db: Session,
    transaction_id: int
):

    return (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.id == transaction_id
        )
        .first()
    )


from sqlalchemy.orm import Session

from app.models.inventory_transaction import (
    InventoryTransaction
)


def get_transactions(
    db: Session,
    product_id: int | None = None,
    warehouse_id: int | None = None,
    transaction_type=None,
    skip: int = 0,
    limit: int = 20,
):
    query = db.query(InventoryTransaction)

    # Filter by product
    if product_id is not None:
        query = query.filter(
            InventoryTransaction.product_id
            == product_id
        )

    # Filter by warehouse
    if warehouse_id is not None:
        query = query.filter(
            InventoryTransaction.warehouse_id
            == warehouse_id
        )

    # Filter by transaction type
    if transaction_type is not None:
        query = query.filter(
            InventoryTransaction.transaction_type
            == transaction_type
        )

    # Newest transactions first
    return (
        query
        .order_by(
            InventoryTransaction.created_at.desc(),
            InventoryTransaction.id.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )