from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    notification: Notification
):
    db.add(notification)
    db.flush()

    return notification


def get_notification_by_id(
    db: Session,
    notification_id: int
):
    return (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )


def get_user_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False
):
    query = db.query(Notification).filter(
        Notification.user_id == user_id
    )

    if unread_only:
        query = query.filter(
            Notification.is_read.is_(False)
        )

    return (
        query
        .order_by(
            Notification.created_at.desc(),
            Notification.id.desc()
        )
        .all()
    )


def count_unread_notifications(
    db: Session,
    user_id: int
):
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False)
        )
        .count()
    )


def mark_notification_read(
    db: Session,
    notification: Notification
):
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.flush()

    return notification


def mark_all_notifications_read(
    db: Session,
    user_id: int
):
    now = datetime.utcnow()

    updated_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False)
        )
        .update(
            {
                Notification.is_read: True,
                Notification.read_at: now
            },
            synchronize_session=False
        )
    )

    db.flush()

    return updated_count