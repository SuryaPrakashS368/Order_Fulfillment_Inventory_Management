from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    audit_log: AuditLog,
) -> AuditLog:
    db.add(audit_log)
    db.flush()
    return audit_log


def get_audit_log_by_id(
    db: Session,
    audit_log_id: int,
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.id == audit_log_id)
        .first()
    )


def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    user_id: int | None = None,
    action: str | None = None,
    entity: str | None = None,
    entity_id: int | None = None,
):
    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if entity:
        query = query.filter(
            AuditLog.entity == entity
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    return (
        query.order_by(desc(AuditLog.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )