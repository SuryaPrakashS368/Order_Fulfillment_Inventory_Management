from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification

from app.repositories.notification_repository import (
    create_notification,
    get_notification_by_id,
    get_user_notifications,
    count_unread_notifications,
    mark_notification_read,
    mark_all_notifications_read
)


def create_notification_service(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    reference_entity: str | None = None,
    reference_id: int | None = None
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_entity=reference_entity,
        reference_id=reference_id,
        is_read=False
    )

    create_notification(db, notification)

    return notification


def get_user_notifications_service(
    db: Session,
    user_id: int,
    unread_only: bool = False
):
    return get_user_notifications(
        db,
        user_id,
        unread_only
    )


def get_unread_count_service(
    db: Session,
    user_id: int
):
    return count_unread_notifications(
        db,
        user_id
    )


def mark_notification_read_service(
    db: Session,
    notification_id: int,
    user_id: int
):
    notification = get_notification_by_id(
        db,
        notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this notification"
        )

    try:
        mark_notification_read(db, notification)
        db.commit()
        db.refresh(notification)

        return notification

    except Exception:
        db.rollback()
        raise


def mark_all_notifications_read_service(
    db: Session,
    user_id: int
):
    try:
        updated_count = mark_all_notifications_read(
            db,
            user_id
        )

        db.commit()

        return updated_count

    except Exception:
        db.rollback()
        raise