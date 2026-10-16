from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.models.return_model import ReturnStatus

from app.repositories.return_repository import (
    get_return_by_id
)


def review_return_service(
    db: Session,
    return_id: int,
    reviewer_id: int,
    reviewer_role: str,
    approved: bool,
    reason: str | None = None
):
    if reviewer_role not in {
        Roles.ADMIN,
        Roles.WAREHOUSE_MANAGER
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot review return requests"
        )

    return_record = get_return_by_id(
        db,
        return_id
    )

    if not return_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )

    if return_record.status != ReturnStatus.REQUESTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only requested returns can be reviewed"
        )

    try:
        return_record.status = (
            ReturnStatus.APPROVED
            if approved
            else ReturnStatus.REJECTED
        )

        return_record.reviewed_by = reviewer_id

        if reason:
            return_record.reason = (
                f"{return_record.reason}\nReview: {reason}"
            )

        db.commit()
        db.refresh(return_record)

        return return_record

    except Exception:
        db.rollback()
        raise