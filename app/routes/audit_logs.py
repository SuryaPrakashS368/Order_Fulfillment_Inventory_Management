from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.constants import Roles
from app.dependencies.auth import get_current_user
from app.core.permissions_dependency import require_permission
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log_service import (
    get_audit_logs_service,
    get_audit_log_service,
)


router = APIRouter(
    prefix="/api/audit-logs",
    tags=["Audit Logs"],
)


def ensure_admin(current_user):
    if current_user.role.name != Roles.ADMIN:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin can access audit logs",
        )


@router.get(
    "",
    response_model=list[AuditLogResponse],
)
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int | None = Query(None, gt=0),
    action: str | None = Query(None, min_length=1),
    entity: str | None = Query(None, min_length=1),
    entity_id: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    permission=Depends(require_permission("audit:read")),
):
    ensure_admin(current_user)

    return get_audit_logs_service(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
    )


@router.get(
    "/{audit_log_id}",
    response_model=AuditLogResponse,
)
def get_audit_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    permission=Depends(require_permission("audit:read")),
):
    ensure_admin(current_user)

    return get_audit_log_service(
        db=db,
        audit_log_id=audit_log_id,
    )