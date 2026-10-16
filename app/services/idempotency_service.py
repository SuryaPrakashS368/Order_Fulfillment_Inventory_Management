import hashlib
import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.idempotency_repository import (
    get_idempotency_key,
)


def generate_request_hash(payload) -> str:
    if hasattr(payload, "model_dump"):
        payload_data = payload.model_dump(mode="json")
    elif isinstance(payload, dict):
        payload_data = payload
    else:
        raise ValueError("Unsupported request payload")

    canonical_json = json.dumps(
        payload_data,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()


def get_existing_idempotent_resource(
    db: Session,
    user_id: int,
    key: str,
    request_hash: str,
):
    record = get_idempotency_key(
        db=db,
        user_id=user_id,
        key=key,
    )

    if record is None:
        return None

    if record.request_hash != request_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This Idempotency-Key was already used "
                "with a different request payload"
            ),
        )

    if record.resource_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A request with this Idempotency-Key "
                "is already being processed. Please retry."
            ),
        )

    if record.resource_type != "Order":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency key belongs to another resource",
        )

    return record.resource_id