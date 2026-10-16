from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import (
    create_audit_log,
    get_audit_log_by_id,
    get_audit_logs,
)


def create_audit_log_service(
    db: Session,
    user_id: int | None,
    action: str,
    entity: str,
    entity_id: int | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )

    return create_audit_log(db, audit_log)


def get_audit_logs_service(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    user_id: int | None = None,
    action: str | None = None,
    entity: str | None = None,
    entity_id: int | None = None,
):
    return get_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
    )


def get_audit_log_service(
    db: Session,
    audit_log_id: int,
) -> AuditLog:
    audit_log = get_audit_log_by_id(
        db,
        audit_log_id,
    )

    if audit_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return audit_log