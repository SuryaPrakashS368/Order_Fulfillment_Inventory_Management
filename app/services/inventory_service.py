from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import Inventory

from app.repositories.inventory_repository import (
    get_inventory_by_id,
    get_inventory_by_product_and_warehouse,
    get_inventory,
    get_inventory_by_warehouse,
    get_inventory_by_product,
    create_inventory,
    update_inventory
)

from app.repositories.product_repository import (
    get_product_by_id
)

from app.repositories.warehouse_repository import (
    get_warehouse_by_id
)


def create_inventory_service(
    db: Session,
    product_id: int,
    warehouse_id: int,
    available_quantity: int,
    reorder_level: int
):

    product = get_product_by_id(
        db,
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not product.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create inventory for inactive product"
        )

    warehouse = get_warehouse_by_id(
        db,
        warehouse_id
    )

    if not warehouse:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    if not warehouse.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create inventory for inactive warehouse"
        )

    existing_inventory = (
        get_inventory_by_product_and_warehouse(
            db,
            product_id,
            warehouse_id
        )
    )

    if existing_inventory:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Inventory already exists "
                "for this product in this warehouse"
            )
        )

    inventory = Inventory(

        product_id=product_id,

        warehouse_id=warehouse_id,

        available_quantity=available_quantity,

        reserved_quantity=0,

        damaged_quantity=0,

        reorder_level=reorder_level
    )

    return create_inventory(
        db,
        inventory
    )


def list_inventory_service(
    db: Session,
    product_id: int | None = None,
    warehouse_id: int | None = None
):

    return get_inventory(
        db,
        product_id=product_id,
        warehouse_id=warehouse_id
    )


def get_inventory_service(
    db: Session,
    inventory_id: int
):

    inventory = get_inventory_by_id(
        db,
        inventory_id
    )

    if not inventory:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    return inventory


def update_inventory_service(
    db: Session,
    inventory_id: int,
    reorder_level: int
):

    inventory = get_inventory_service(
        db,
        inventory_id
    )

    inventory.reorder_level = reorder_level

    return update_inventory(
        db,
        inventory
    )


def get_warehouse_inventory_service(
    db: Session,
    warehouse_id: int
):

    warehouse = get_warehouse_by_id(
        db,
        warehouse_id
    )

    if not warehouse:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    return get_inventory_by_warehouse(
        db,
        warehouse_id
    )


def get_product_inventory_service(
    db: Session,
    product_id: int
):

    product = get_product_by_id(
        db,
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return get_inventory_by_product(
        db,
        product_id
    )