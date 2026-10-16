from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.core.database import get_db


from app.core.permissions_dependency import require_permission
from app.schemas.user import (
    AdminCreateUserRequest,
    UserUpdateRequest,
    UserStatusRequest,
    UserResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.user_service import (
    create_user_by_admin,
    list_users,
    get_user,
    update_user_details,
    update_user_status
)


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    request: AdminCreateUserRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("user:create")
    )
):

    user = create_user_by_admin(
        db,
        request
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="USER_CREATED_BY_ADMIN",
        entity="User",
        entity_id=user.id,
        details={
            "role": user.role.name,
            "is_active": user.is_active
        }
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.name,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.get(
    "",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("user:read")
    )
):
    users = list_users(db)

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.name if user.role else None,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ]



@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_single_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("user:read")
    )
):

    user = get_user(
        db,
        user_id
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.name,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("user:update")
    )
):

    user = update_user_details(
        db,
        user_id,
        request.name,
        request.email
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.name,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse
)
def update_user_status_route(
    user_id: int,
    request: UserStatusRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("user:deactivate")
    )
):

    user = update_user_status(
        db=db,
        user_id=user_id,
        is_active=request.is_active
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.name,
        "is_active": user.is_active,
        "created_at": user.created_at
    }