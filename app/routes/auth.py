from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import (
    get_current_user
)

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    LogoutRequest,
    ChangePasswordRequest,
    UserResponse,
    TokenResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
    logout_user,
    change_password
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    user = register_user(
        db,
        request
    )

    create_audit_log_service(
        db=db,
        user_id=user.id,
        action="USER_REGISTERED",
        entity="User",
        entity_id=user.id,
        details={
            "role": user.role.name
        }
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.name,
        "is_active": user.is_active
    }


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    return login_user(
        db,
        request.email,
        request.password
    )


@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):

    return refresh_access_token(
        db,
        request.refresh_token
    )


@router.post(
    "/logout"
)
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db)
):

    return logout_user(
        db,
        request.refresh_token
    )


@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user=Depends(
        get_current_user
    )
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.name,
        "is_active": current_user.is_active
    }


@router.post(
    "/change-password"
)
def change_user_password(
    request: ChangePasswordRequest,
    current_user=Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    return change_password(
        db,
        current_user,
        request.current_password,
        request.new_password
    )