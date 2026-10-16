
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions_dependency import require_permission

from app.models.payment import Payment
from app.schemas.payment import (
    PaymentConfirmRequest,
    PaymentResponse,
)
from app.repositories.payment_repository import (
    get_payment_by_id,
)
from app.services.audit_log_service import create_audit_log_service
from app.services.notification_service import create_notification_service
from app.services.payment_service import (
    confirm_payment_service,
)


router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"],
)


def is_admin_user(user) -> bool:
    role_name = getattr(
        getattr(user, "role", None),
        "name",
        "",
    )
    return role_name.upper().replace(" ", "_") == "ADMIN"


@router.post(
    "/confirm",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def confirm_payment(
    request: PaymentConfirmRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=255,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("payment:confirm")
    ),
):
    payment = confirm_payment_service(
        db=db,
        order_id=request.order_id,
        customer_id=current_user.id,
        payment_method=request.payment_method,
        idempotency_key=idempotency_key,
        is_admin=is_admin_user(current_user)
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="PAYMENT_CONFIRMED",
        entity="Payment",
        entity_id=payment.id,
        details={
            "order_id": request.order_id,
            "payment_method": request.payment_method,
            "status": str(payment.status)
        }
    )

    create_notification_service(
        db=db,
        user_id=payment.customer_id,
        title="Payment Update",
        message=f"Payment for order #{request.order_id} was processed.",
        notification_type="PAYMENT_CONFIRMED",
        reference_entity="Order",
        reference_id=request.order_id
    )

    return payment


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("payment:read")
    ),
):
    payment = get_payment_by_id(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    if (
        not is_admin_user(current_user)
        and payment.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot access this payment",
        )

    return payment
