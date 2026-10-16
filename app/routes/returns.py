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

from app.repositories.return_repository import (
    get_return_by_id
)

from app.repositories.warehouse_user_repository import (
    get_assignment as get_warehouse_assignment
)

from app.schemas.return_schema import (
    ReturnCreate,
    ReturnReviewRequest,
    ReturnDetailResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.notification_service import create_notification_service
from app.services.return_service import (
    create_return_service,
    get_customer_returns_service,
    get_all_returns_service,
    get_return_service
)

from app.services.return_review_service import (
    review_return_service
)

from app.services.return_receive_service import (
    receive_return_service,
    refund_return_service
)


router = APIRouter(
    prefix="/api/returns",
    tags=["Returns"]
)


def check_return_access(
    db: Session,
    return_record,
    current_user
):
    if current_user.role.name == Roles.ADMIN:
        return

    if current_user.role.name == Roles.CUSTOMER:
        if return_record.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access this return"
            )
        return

    assignment = get_warehouse_assignment(
        db,
        return_record.order.warehouse_id,
        current_user.id
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this warehouse"
        )


@router.post(
    "",
    response_model=ReturnDetailResponse,
    status_code=status.HTTP_201_CREATED
)
def create_return(
    request: ReturnCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("return:create")
    )
):
    return_record = create_return_service(
        db=db,
        order_id=request.order_id,
        customer_id=current_user.id,
        reason=request.reason,
        items=request.items
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="RETURN_CREATED",
        entity="Return",
        entity_id=return_record.id,
        details={
            "order_id": request.order_id,
            "reason": request.reason
        }
    )

    create_notification_service(
        db=db,
        user_id=return_record.customer_id,
        title="Return Request Created",
        message=f"Return request #{return_record.id} was submitted.",
        notification_type="RETURN_CREATED",
        reference_entity="Return",
        reference_id=return_record.id
    )

    return return_record


@router.get(
    "/my-returns",
    response_model=list[ReturnDetailResponse]
)
def get_my_returns(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role.name != Roles.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is for customers"
        )

    return get_customer_returns_service(
        db,
        current_user.id
    )


@router.get(
    "",
    response_model=list[ReturnDetailResponse]
)
def get_returns(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("return:approve")
    )
):
    if current_user.role.name == Roles.ADMIN:
        return get_all_returns_service(db)

    if current_user.role.name != Roles.WAREHOUSE_MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot view all return requests"
        )

    # Warehouse managers see only returns for their assigned
    # warehouses. Filter before returning the response.
    records = get_all_returns_service(db)

    return [
        record
        for record in records
        if get_warehouse_assignment(
            db,
            record.order.warehouse_id,
            current_user.id
        )
    ]


@router.get(
    "/{return_id}",
    response_model=ReturnDetailResponse
)
def get_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return_record = get_return_service(
        db,
        return_id
    )

    check_return_access(
        db,
        return_record,
        current_user
    )

    return return_record


@router.post(
    "/{return_id}/approve",
    response_model=ReturnDetailResponse
)
def approve_return(
    return_id: int,
    request: ReturnReviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("return:approve")
    )
):
    return_record = get_return_by_id(
        db,
        return_id
    )

    if not return_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    check_return_access(
        db,
        return_record,
        current_user
    )

    reviewed_return = review_return_service(
        db=db,
        return_id=return_id,
        reviewer_id=current_user.id,
        reviewer_role=current_user.role.name,
        approved=True,
        reason=request.reason
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="RETURN_APPROVED",
        entity="Return",
        entity_id=return_id,
        details={"reason": request.reason}
    )

    create_notification_service(
        db=db,
        user_id=return_record.customer_id,
        title="Return Approved",
        message=f"Return request #{return_id} was approved.",
        notification_type="RETURN_APPROVED",
        reference_entity="Return",
        reference_id=return_id
    )

    return reviewed_return


@router.post(
    "/{return_id}/reject",
    response_model=ReturnDetailResponse
)
def reject_return(
    return_id: int,
    request: ReturnReviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("return:approve")
    )
):
    return_record = get_return_by_id(
        db,
        return_id
    )

    if not return_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    check_return_access(
        db,
        return_record,
        current_user
    )

    return review_return_service(
        db=db,
        return_id=return_id,
        reviewer_id=current_user.id,
        reviewer_role=current_user.role.name,
        approved=False,
        reason=request.reason
    )


@router.post(
    "/{return_id}/receive",
    response_model=ReturnDetailResponse
)
def receive_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("return:receive")
    )
):
    return_record = get_return_by_id(
        db,
        return_id
    )

    if not return_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    check_return_access(
        db,
        return_record,
        current_user
    )

    received_return = receive_return_service(
        db=db,
        return_id=return_id,
        receiver_id=current_user.id,
        receiver_role=current_user.role.name
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="RETURN_RECEIVED",
        entity="Return",
        entity_id=return_id,
        details={}
    )

    create_notification_service(
        db=db,
        user_id=return_record.customer_id,
        title="Return Received",
        message=f"Return request #{return_id} was received.",
        notification_type="RETURN_RECEIVED",
        reference_entity="Return",
        reference_id=return_id
    )

    return received_return


@router.post(
    "/{return_id}/refund",
    response_model=ReturnDetailResponse
)
def refund_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("return:approve")
    )
):
    refunded_return = refund_return_service(
        db=db,
        return_id=return_id,
        reviewer_role=current_user.role.name
    )

    return_record = get_return_by_id(db, return_id)

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="RETURN_REFUNDED",
        entity="Return",
        entity_id=return_id,
        details={}
    )

    create_notification_service(
        db=db,
        user_id=return_record.customer_id,
        title="Refund Update",
        message=f"Refund for return #{return_id} was processed.",
        notification_type="RETURN_REFUNDED",
        reference_entity="Return",
        reference_id=return_id
    )

    return refunded_return