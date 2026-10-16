from fastapi import (
    APIRouter,
    Depends,
    Header,
    Query,
    status,
    HTTPException
)
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.core.database import get_db

from app.core.permissions_dependency import require_permission
from app.dependencies.order import (
    get_accessible_order
)

from app.schemas.order import (
    OrderCancellationRequest,
    OrderCancellationResponse,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    OrderStatusHistoryResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.notification_service import create_notification_service
from app.services.order_cancellation_service import cancel_order_service
from app.services.order_service import (
    create_order_service,
    get_order_service,
    get_customer_orders_service
)

from app.services.order_state_service import (
    update_order_status_service,
    get_order_status_history_service
)
import hashlib
import json


router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)

def calculate_request_hash(payload) -> str:
    if hasattr(payload, "model_dump"):
        payload_data = payload.model_dump(mode="json")
    else:
        payload_data = payload.dict()

    canonical_json = json.dumps(
        payload_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    request: OrderCreate,
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("order:create")
    ),
):
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Idempotency-Key header. Send it in the request headers."
        )

    request_hash = calculate_request_hash(request)

    order = create_order_service(
    db=db,
    customer_id=current_user.id,
    warehouse_id=request.warehouse_id,
    items=request.items,
    idempotency_key=idempotency_key,
    request_hash=request_hash
)

# Create audit log
    create_audit_log_service(
    db=db,
    user_id=current_user.id,
    action="ORDER_CREATED",
    entity="Order",
    entity_id=order.id,
    details={
        "warehouse_id": order.warehouse_id,
        "status": str(order.status)
    }
    )

# Create notification only for a newly created order.
    create_notification_service(
    db=db,
    user_id=current_user.id,
    title="Order Created",
    message=f"Your order #{order.id} has been created.",
    notification_type="ORDER_CREATED",
    reference_entity="Order",
    reference_id=order.id
    )
    return order

@router.get("", response_model=list[OrderResponse])
def list_orders(
    order_status: str | None = Query(
        default=None,
        alias="status"
    ),
    order_number: str | None = Query(
        default=None,
        min_length=1,
        max_length=100
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
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("order:read")
    ),
):
    return get_customer_orders_service(
        db=db,
        customer_id=current_user.id,
        order_status=order_status,
        order_number=order_number,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{order_id}/history",
    response_model=list[OrderStatusHistoryResponse]
)
def get_order_history(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("order:read")
    )
):
    get_accessible_order(
        order_id=order_id,
        db=db,
        current_user=current_user
    )

    return get_order_status_history_service(
        db,
        order_id
    )


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse
)
def update_order_status(
    order_id: int,
    request: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("order:update")
    )
):
    order = get_accessible_order(
        order_id=order_id,
        db=db,
        current_user=current_user
    )

    if current_user.role.name == Roles.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Customers cannot directly "
                "change order status"
            )
        )

    old_status = str(order.status)

    updated_order = update_order_status_service(
        db=db,
        order_id=order_id,
        new_status=request.status,
        changed_by=current_user.id,
        role_name=current_user.role.name,
        reason=request.reason
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="ORDER_STATUS_CHANGED",
        entity="Order",
        entity_id=updated_order.id,
        details={
            "old_status": old_status,
            "new_status": str(updated_order.status),
            "reason": request.reason
        }
    )

    create_notification_service(
        db=db,
        user_id=updated_order.customer_id,
        title="Order Status Updated",
        message=(
            f"Order #{updated_order.id} status changed "
            f"to {updated_order.status}."
        ),
        notification_type="ORDER_STATUS_CHANGED",
        reference_entity="Order",
        reference_id=updated_order.id
    )

    return updated_order


@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("order:read")
    )
):
    order = get_order_service(
        db,
        order_id
    )

    if (
        current_user.role.name != Roles.ADMIN
        and order.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this order"
        )

    return order


@router.post(
    "/{order_id}/cancel",
    response_model=OrderCancellationResponse
)
def cancel_order(
    order_id: int,
    request: OrderCancellationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("order:cancel")
    )
):
    # Customers can access only their own orders.
    # Operational users must have access to the order's warehouse.
    get_accessible_order(
        order_id=order_id,
        db=db,
        current_user=current_user
    )

    cancelled_order = cancel_order_service(
        db=db,
        order_id=order_id,
        user_id=current_user.id,
        reason=request.reason
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="ORDER_CANCELLED",
        entity="Order",
        entity_id=order_id,
        details={"reason": request.reason}
    )

    create_notification_service(
        db=db,
        user_id=cancelled_order.customer_id,
        title="Order Cancelled",
        message=f"Order #{order_id} has been cancelled.",
        notification_type="ORDER_CANCELLED",
        reference_entity="Order",
        reference_id=order_id
    )

    return cancelled_order