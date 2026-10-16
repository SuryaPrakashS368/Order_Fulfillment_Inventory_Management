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

from app.repositories.warehouse_user_repository import (
    get_assignment
)

from app.schemas.inventory_transaction import (
    InventoryAdjustmentRequest,
    InventoryPurchaseRequest,
    InventoryDamageRequest,
    InventoryTransactionResponse
)

from app.models.inventory_transaction import (
    InventoryTransactionType
)

from app.services.audit_log_service import create_audit_log_service
from app.services.inventory_transaction_service import (
    adjust_inventory_service,
    purchase_inventory_service,
    damage_inventory_service,
    list_inventory_transactions_service
)


router = APIRouter(
    prefix="/api/inventory/transactions",
    tags=["Inventory Transactions"]
)


def check_warehouse_access(
    db: Session,
    warehouse_id: int,
    current_user
):

    if current_user.role.name == Roles.ADMIN:

        return

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


@router.post(
    "/adjust",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def adjust_inventory(
    request: InventoryAdjustmentRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("inventory:adjust")
    )
):

    check_warehouse_access(
        db,
        request.warehouse_id,
        current_user
    )

    transaction = adjust_inventory_service(
        db,
        request.product_id,
        request.warehouse_id,
        request.quantity,
        request.reason,
        current_user.id
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="INVENTORY_ADJUSTED",
        entity="InventoryTransaction",
        entity_id=transaction.id,
        details={
            "product_id": request.product_id,
            "warehouse_id": request.warehouse_id,
            "quantity": request.quantity,
            "reason": request.reason
        }
    )

    return transaction


@router.post(
    "/purchase",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def purchase_inventory(
    request: InventoryPurchaseRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("inventory:adjust")
    )
):

    check_warehouse_access(
        db,
        request.warehouse_id,
        current_user
    )

    transaction = purchase_inventory_service(
        db,
        request.product_id,
        request.warehouse_id,
        request.quantity,
        request.reason,
        current_user.id
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="INVENTORY_PURCHASE_RECEIVED",
        entity="InventoryTransaction",
        entity_id=transaction.id,
        details={
            "product_id": request.product_id,
            "warehouse_id": request.warehouse_id,
            "quantity": request.quantity,
            "reason": request.reason
        }
    )

    return transaction


@router.post(
    "/damage",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def damage_inventory(
    request: InventoryDamageRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("inventory:adjust")
    )
):

    check_warehouse_access(
        db,
        request.warehouse_id,
        current_user
    )

    transaction = damage_inventory_service(
        db,
        request.product_id,
        request.warehouse_id,
        request.quantity,
        request.reason,
        current_user.id
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="INVENTORY_DAMAGED",
        entity="InventoryTransaction",
        entity_id=transaction.id,
        details={
            "product_id": request.product_id,
            "warehouse_id": request.warehouse_id,
            "quantity": request.quantity,
            "reason": request.reason
        }
    )

    return transaction


@router.get(
    "",
    response_model=list[InventoryTransactionResponse]
)
def get_inventory_transactions(
    product_id: int | None = Query(
        default=None,
        gt=0
    ),
    warehouse_id: int | None = Query(
        default=None,
        gt=0
    ),
    transaction_type: InventoryTransactionType | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("inventory:read")
    ),
    skip: int = Query(
    default=0,
    ge=0
    ),
    limit: int = Query(
    default=20,
    ge=1,
    le=100
    ),
):

    if warehouse_id is not None:

        check_warehouse_access(
            db,
            warehouse_id,
            current_user
        )

    return list_inventory_transactions_service(
        db,
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=transaction_type,
        skip=skip,
        limit=limit,
    )