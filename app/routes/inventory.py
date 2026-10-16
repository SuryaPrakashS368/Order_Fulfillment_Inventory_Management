from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.constants import Roles

from app.core.permissions_dependency import require_permission

from app.dependencies.warehouse import (
    get_current_warehouse
)

from app.repositories.warehouse_repository import (
    get_warehouse_by_id
)

from app.repositories.warehouse_user_repository import (
    get_assignment
)

from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.inventory_service import (
    create_inventory_service,
    list_inventory_service,
    get_inventory_service,
    update_inventory_service,
    get_warehouse_inventory_service,
    get_product_inventory_service
)


router = APIRouter(
    prefix="/api/inventory",
    tags=["Inventory"]
)


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_inventory(
    request: InventoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("inventory:adjust")
    )
):

    warehouse = get_warehouse_by_id(
        db,
        request.warehouse_id
    )

    if not warehouse:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    if not warehouse.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warehouse is inactive"
        )

    if current_user.role.name != Roles.ADMIN:

        assignment = get_assignment(
            db,
            request.warehouse_id,
            current_user.id
        )

        if not assignment:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to this warehouse"
            )

    inventory = create_inventory_service(
        db,
        request.product_id,
        request.warehouse_id,
        request.available_quantity,
        request.reorder_level
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="INVENTORY_CREATED",
        entity="Inventory",
        entity_id=inventory.id,
        details={
            "product_id": request.product_id,
            "warehouse_id": request.warehouse_id,
            "available_quantity": request.available_quantity,
            "reorder_level": request.reorder_level
        }
    )

    return inventory


@router.get(
    "",
    response_model=list[InventoryResponse]
)
def get_inventory(
    product_id: int | None = Query(
        default=None,
        gt=0
    ),
    warehouse_id: int | None = Query(
        default=None,
        gt=0
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("inventory:read")
    )
):

    if warehouse_id is not None:

        if current_user.role.name != Roles.ADMIN:

            assignment = get_assignment(
                db,
                warehouse_id,
                current_user.id
            )

            if not assignment:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not assigned to this warehouse"
                )

    return list_inventory_service(
        db,
        product_id=product_id,
        warehouse_id=warehouse_id
    )


@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse
)
def get_single_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("inventory:read")
    )
):

    inventory = get_inventory_service(
        db,
        inventory_id
    )

    if current_user.role.name != Roles.ADMIN:

        assignment = get_assignment(
            db,
            inventory.warehouse_id,
            current_user.id
        )

        if not assignment:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to this warehouse"
            )

    return inventory


@router.put(
    "/{inventory_id}",
    response_model=InventoryResponse
)
def update_inventory(
    inventory_id: int,
    request: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("inventory:adjust")
    )
):

    inventory = get_inventory_service(
        db,
        inventory_id
    )

    if current_user.role.name != Roles.ADMIN:

        assignment = get_assignment(
            db,
            inventory.warehouse_id,
            current_user.id
        )

        if not assignment:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to this warehouse"
            )

    old_reorder_level = inventory.reorder_level

    updated_inventory = update_inventory_service(
        db,
        inventory_id,
        request.reorder_level
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="INVENTORY_REORDER_LEVEL_UPDATED",
        entity="Inventory",
        entity_id=inventory_id,
        details={
            "old_reorder_level": old_reorder_level,
            "new_reorder_level": request.reorder_level
        }
    )

    return updated_inventory


@router.get(
    "/warehouse/{warehouse_id}",
    response_model=list[InventoryResponse]
)
def get_warehouse_inventory(
    warehouse=Depends(
        get_current_warehouse
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("inventory:read")
    )
):

    return get_warehouse_inventory_service(
        db,
        warehouse.id
    )


@router.get(
    "/product/{product_id}",
    response_model=list[InventoryResponse]
)
def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("inventory:read")
    )
):

    inventories = get_product_inventory_service(
        db,
        product_id
    )

    if current_user.role.name == Roles.ADMIN:

        return inventories

    allowed_inventories = []

    for inventory in inventories:

        assignment = get_assignment(
            db,
            inventory.warehouse_id,
            current_user.id
        )

        if assignment:

            allowed_inventories.append(
                inventory
            )

    return allowed_inventories