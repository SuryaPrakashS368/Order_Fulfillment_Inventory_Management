from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import get_current_user
from app.core.permissions_dependency import require_permission

from app.schemas.notification import (
    NotificationResponse,
    UnreadNotificationCountResponse,
    NotificationMessageResponse
)

from app.services.notification_service import (
    get_user_notifications_service,
    get_unread_count_service,
    mark_notification_read_service,
    mark_all_notifications_read_service
)


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_my_notifications(
    unread_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("notification:read")
    )
):
    return get_user_notifications_service(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only
    )


@router.get(
    "/unread-count",
    response_model=UnreadNotificationCountResponse
)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("notification:read")
    )
):
    count = get_unread_count_service(
        db,
        current_user.id
    )

    return {
        "unread_count": count
    }


@router.patch(
    "/read-all",
    response_model=NotificationMessageResponse
)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("notification:read")
    )
):
    count = mark_all_notifications_read_service(
        db,
        current_user.id
    )

    return {
        "message": "Notifications marked as read",
        "updated_count": count
    }


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def mark_one_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("notification:read")
    )
):
    return mark_notification_read_service(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )