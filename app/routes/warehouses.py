from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.permissions_dependency import require_permission

from app.dependencies.warehouse import (
    get_current_warehouse
)

from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseStatusUpdate,
    WarehouseResponse,
    WarehouseUserResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.warehouse_service import (
    create_warehouse_service,
    list_warehouses,
    update_warehouse_service,
    update_warehouse_status,
    assign_user_to_warehouse,
    remove_user_from_warehouse,
    list_warehouse_users
)

from app.core.constants import Roles


router = APIRouter(
    prefix="/api/warehouses",
    tags=["Warehouses"]
)


@router.post(
    "",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_warehouse(
    request: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("warehouse:create")
    )
):

    warehouse = create_warehouse_service(
        db,
        request.name,
        request.location,
        request.capacity
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="WAREHOUSE_CREATED",
        entity="Warehouse",
        entity_id=warehouse.id,
        details={
            "name": warehouse.name,
            "location": warehouse.location
        }
    )

    return warehouse


@router.get(
    "",
    response_model=list[WarehouseResponse]
)
def get_warehouses(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("warehouse:read")
    )
):

    if current_user.role.name == Roles.ADMIN:

        return list_warehouses(db)

    assignments = (
        current_user.warehouse_assignments
    )

    return [
        assignment.warehouse
        for assignment in assignments
        if assignment.warehouse.is_active
    ]


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse
)
def get_single_warehouse(
    warehouse=Depends(
        get_current_warehouse
    ),
    current_user=Depends(
        require_permission("warehouse:read")
    )
):

    return warehouse


@router.put(
    "/{warehouse_id}",
    response_model=WarehouseResponse
)
def update_warehouse(
    request: WarehouseUpdate,
    warehouse=Depends(
        get_current_warehouse
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("warehouse:update")
    )
):

    return update_warehouse_service(
        db,
        warehouse.id,
        request.name,
        request.location,
        request.capacity
    )


@router.patch(
    "/{warehouse_id}/status",
    response_model=WarehouseResponse
)
def update_warehouse_status_route(
    request: WarehouseStatusUpdate,
    warehouse=Depends(
        get_current_warehouse
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("warehouse:update")
    )
):

    return update_warehouse_status(
        db,
        warehouse.id,
        request.is_active
    )


@router.post(
    "/{warehouse_id}/users/{user_id}",
    status_code=status.HTTP_201_CREATED
)
def assign_user(
    user_id: int,
    warehouse=Depends(
        get_current_warehouse
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            "warehouse:assign_user"
        )
    )
):

    assignment = assign_user_to_warehouse(
        db,
        warehouse.id,
        user_id
    )

    return {
        "message": "User assigned successfully",
        "warehouse_id": assignment.warehouse_id,
        "user_id": assignment.user_id
    }


@router.delete(
    "/{warehouse_id}/users/{user_id}"
)
def remove_user(
    user_id: int,
    warehouse=Depends(
        get_current_warehouse
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            "warehouse:assign_user"
        )
    )
):

    return remove_user_from_warehouse(
        db,
        warehouse.id,
        user_id
    )


@router.get(
    "/{warehouse_id}/users",
    response_model=list[WarehouseUserResponse]
)
def get_warehouse_users(
    warehouse=Depends(
        get_current_warehouse
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("warehouse:read")
    )
):

    return list_warehouse_users(
        db,
        warehouse.id
    )