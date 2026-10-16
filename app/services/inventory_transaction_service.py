from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.models.inventory import Inventory

from app.models.inventory_transaction import (
    InventoryTransaction,
    InventoryTransactionType
)

from app.repositories.inventory_repository import (
    get_inventory_by_product_and_warehouse,
    get_inventory_for_update
)

from app.repositories.inventory_transaction_repository import (
    create_transaction,
    get_transactions
)


def adjust_inventory_service(
    db: Session,
    product_id: int,
    warehouse_id: int,
    quantity: int,
    reason: str,
    user_id: int
):

    inventory = get_inventory_for_update(
    db=db,
    product_id=product_id,
    warehouse_id=warehouse_id,
)

    if not inventory:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    new_quantity = (
        inventory.available_quantity
        + quantity
    )

    if new_quantity < 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Available inventory cannot become negative"
        )

    inventory.available_quantity = (
        new_quantity
    )

    transaction = InventoryTransaction(
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=(
            InventoryTransactionType.ADJUSTMENT
        ),
        quantity=quantity,
        reference_entity="Inventory",
        reference_id=inventory.id,
        user_id=user_id,
        transaction_metadata={
            "reason": reason
        }
    )

    create_transaction(
        db,
        transaction
    )

    db.flush()

    return transaction


def purchase_inventory_service(
    db: Session,
    product_id: int,
    warehouse_id: int,
    quantity: int,
    reason: str | None,
    user_id: int
):

    inventory = get_inventory_for_update(
    db=db,
    product_id=product_id,
    warehouse_id=warehouse_id,
)

    if not inventory:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )
    
    if quantity <= 0:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Purchase quantity must be positive"
    )

    inventory.available_quantity += quantity

    transaction = InventoryTransaction(
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=(
            InventoryTransactionType.PURCHASE
        ),
        quantity=quantity,
        reference_entity="Inventory",
        reference_id=inventory.id,
        user_id=user_id,
        transaction_metadata={
            "reason": reason
        }
    )

    create_transaction(
        db,
        transaction
    )

    db.flush()

    return transaction


def damage_inventory_service(
    db: Session,
    product_id: int,
    warehouse_id: int,
    quantity: int,
    reason: str,
    user_id: int
):

    inventory = get_inventory_for_update(
    db=db,
    product_id=product_id,
    warehouse_id=warehouse_id,
)

    if not inventory:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    if inventory.available_quantity < quantity:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient available stock"
        )

    if quantity <= 0:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Damage quantity must be positive"
    )

    inventory.available_quantity -= quantity

    inventory.damaged_quantity += quantity

    transaction = InventoryTransaction(
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=(
            InventoryTransactionType.DAMAGE
        ),
        quantity=quantity,
        reference_entity="Inventory",
        reference_id=inventory.id,
        user_id=user_id,
        transaction_metadata={
            "reason": reason
        }
    )

    create_transaction(
        db,
        transaction
    )

    db.flush()

    return transaction


# def damage_inventory_service(
#     db: Session,
#     product_id: int,
#     warehouse_id: int,
#     quantity: int,
#     reason: str,
#     user_id: int
# ):

#     inventory = (
#         get_inventory_by_product_and_warehouse(
#             db,
#             product_id,
#             warehouse_id
#         )
#     )

#     if not inventory:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Inventory not found"
#         )

#     if inventory.available_quantity < quantity:

#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Insufficient available stock"
#         )

#     inventory.available_quantity -= quantity

#     inventory.damaged_quantity += quantity

#     transaction = InventoryTransaction(

#         product_id=product_id,

#         warehouse_id=warehouse_id,

#         transaction_type=(
#             InventoryTransactionType.DAMAGE
#         ),

#         quantity=quantity,

#         reference_entity="Inventory",

#         reference_id=inventory.id,

#         user_id=user_id,

#         transaction_metadata={
#             "reason": reason
#         }
#     )

#     create_transaction(
#         db,
#         transaction
#     )

#     db.commit()

#     db.refresh(
#         inventory
#     )

#     return transaction


def reserve_inventory_service(
    db: Session,
    product_id: int,
    warehouse_id: int,
    quantity: int,
    order_id: int,
    user_id: int
):

    inventory = get_inventory_for_update(
    db=db,
    product_id=product_id,
    warehouse_id=warehouse_id,
)

    if not inventory:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    if quantity <= 0:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Reservation quantity must be positive"
    )

    if inventory.available_quantity < quantity:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Insufficient available inventory"
        )

    inventory.available_quantity -= quantity

    inventory.reserved_quantity += quantity

    transaction = InventoryTransaction(
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=(
            InventoryTransactionType.RESERVATION
        ),
        quantity=quantity,
        reference_entity="Order",
        reference_id=order_id,
        user_id=user_id,
        transaction_metadata={
            "order_id": order_id
        }
    )

    create_transaction(
        db,
        transaction
    )

    db.flush()

    return transaction

def release_inventory_service(
    db,
    product_id: int,
    warehouse_id: int,
    quantity: int,
    order_id: int,
    user_id: int
):
    inventory = get_inventory_for_update(
    db=db,
    product_id=product_id,
    warehouse_id=warehouse_id,
)

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found"
        )

    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Release quantity must be positive"
        )

    if inventory.reserved_quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Insufficient reserved inventory to release"
        )

    inventory.reserved_quantity -= quantity
    inventory.available_quantity += quantity

    transaction = InventoryTransaction(
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=InventoryTransactionType.RELEASE,
        quantity=quantity,
        reference_entity="Order",
        reference_id=order_id,
        user_id=user_id,
        transaction_metadata={
            "reason": "Order cancellation",
            "order_id": order_id
        }
    )

    create_transaction(db, transaction)
    db.flush()

    return inventory

def list_inventory_transactions_service(
    db: Session,
    product_id: int | None = None,
    warehouse_id: int | None = None,
    transaction_type=None,
    skip: int = 0,
    limit: int = 20,
):
    return get_transactions(
        db=db,
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=transaction_type,
        skip=skip,
        limit=limit,
    )