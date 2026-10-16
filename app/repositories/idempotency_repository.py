from sqlalchemy.orm import Session

from app.models.idempotency_key import IdempotencyKey


def get_idempotency_key(
    db: Session,
    user_id: int,
    key: str,
):
    return (
        db.query(IdempotencyKey)
        .filter(
            IdempotencyKey.user_id == user_id,
            IdempotencyKey.key == key,
        )
        .first()
    )


def create_idempotency_key(
    db: Session,
    user_id: int,
    key: str,
    resource_type: str,
    resource_id: int | None,
    request_hash: str,
) -> IdempotencyKey:
    record = IdempotencyKey(
        user_id=user_id,
        key=key,
        resource_type=resource_type,
        resource_id=resource_id,
        request_hash=request_hash,
    )

    db.add(record)
    db.flush()

    return record


def update_idempotency_resource(
    db: Session,
    record: IdempotencyKey,
    resource_id: int,
) -> IdempotencyKey:
    record.resource_id = resource_id
    db.flush()

    return record