
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions_dependency import require_permission
from app.models.warehouse import Warehouse
from app.models.user import User
from app.models.warehouse_user import WarehouseUser
from app.schemas.warehouse_user import WarehouseUserCreate
from app.services.audit_log_service import create_audit_log_service
from app.services.notification_service import create_notification_service


router = APIRouter(
    prefix="/api/warehouses",
    tags=["Warehouse Users"],
)


@router.post(
    "/{warehouse_id}/users",
    status_code=status.HTTP_201_CREATED,
)
def assign_user_to_warehouse(
    warehouse_id: int,
    request: WarehouseUserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("warehouse:assign_user")
    ),
):
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id
    ).first()

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found",
        )

    user = db.query(User).filter(
        User.id == request.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    existing = db.query(WarehouseUser).filter(
        WarehouseUser.warehouse_id == warehouse_id,
        WarehouseUser.user_id == request.user_id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="User is already assigned to this warehouse",
        )

    assignment = WarehouseUser(
        warehouse_id=warehouse_id,
        user_id=request.user_id,
    )

    try:
        db.add(assignment)
        db.flush()

        create_audit_log_service(
            db=db,
            user_id=current_user.id,
            action="WAREHOUSE_USER_ASSIGNED",
            entity="WarehouseUser",
            entity_id=assignment.id,
            details={
                "warehouse_id": warehouse_id,
                "assigned_user_id": user.id
            }
        )

        create_notification_service(
            db=db,
            user_id=user.id,
            title="Warehouse Assignment",
            message=(
                f"You have been assigned to warehouse "
                f"{warehouse.name}."
            ),
            notification_type="WAREHOUSE_ASSIGNED",
            reference_entity="Warehouse",
            reference_id=warehouse_id
        )

        db.commit()
        db.refresh(assignment)

        return {
            "message": "User assigned to warehouse successfully",
            "id": assignment.id,
            "warehouse_id": assignment.warehouse_id,
            "user_id": assignment.user_id
        }

    except Exception:
        db.rollback()
        raise