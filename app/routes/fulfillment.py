from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.database import get_db

from app.dependencies.auth import get_current_user
from app.core.permissions_dependency import require_permission

from app.repositories.order_repository import (
    get_order_by_id
)

from app.repositories.warehouse_user_repository import (
    get_assignment as get_warehouse_assignment
)

from app.schemas.order_assignment import (
    OrderAssignmentCreate,
    OrderAssignmentResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.fulfillment_service import (
    assign_fulfillment_agent_service,
    get_order_assignments_service,
    get_my_fulfillment_assignments_service
)
from app.services.notification_service import create_notification_service


router = APIRouter(
    prefix="/api/fulfillment",
    tags=["Fulfillment"]
)


@router.post(
    "/orders/{order_id}/assign",
    response_model=OrderAssignmentResponse,
    status_code=status.HTTP_201_CREATED
)
def assign_fulfillment_agent(
    order_id: int,
    request: OrderAssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("order:assign")
    )
):
    assignment = assign_fulfillment_agent_service(
        db=db,
        order_id=order_id,
        agent_id=request.agent_id,
        assigned_by=current_user.id,
        assigned_by_role=current_user.role.name
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="FULFILLMENT_AGENT_ASSIGNED",
        entity="OrderAssignment",
        entity_id=assignment.id,
        details={
            "order_id": order_id,
            "agent_id": request.agent_id
        }
    )

    create_notification_service(
        db=db,
        user_id=request.agent_id,
        title="New Order Assignment",
        message=f"You have been assigned order #{order_id}.",
        notification_type="ORDER_ASSIGNED",
        reference_entity="Order",
        reference_id=order_id
    )

    return assignment


@router.get(
    "/orders/{order_id}/assignments",
    response_model=list[OrderAssignmentResponse]
)
def get_order_assignments(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("order:read")
    )
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if current_user.role.name == Roles.ADMIN:
        pass

    elif current_user.role.name == Roles.CUSTOMER:
        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access this order"
            )

    else:
        assignment = get_warehouse_assignment(
            db,
            order.warehouse_id,
            current_user.id
        )

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this warehouse"
            )

    return get_order_assignments_service(
        db,
        order_id
    )


@router.get(
    "/my-assignments",
    response_model=list[OrderAssignmentResponse]
)
def get_my_assignments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.name != Roles.FULFILLMENT_AGENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only fulfillment agents can access this endpoint"
        )

    return get_my_fulfillment_assignments_service(
        db,
        current_user.id
    )