from datetime import datetime, timedelta

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.core.config import settings

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token
)

from app.core.exceptions import (
    invalid_credentials,
    inactive_user,
    invalid_refresh_token,
    password_mismatch
)

from app.models.user import User

from app.models.role import Role

from app.models.refresh_token import RefreshToken

from app.repositories.user_repository import (
    get_role_by_name,
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_user
)

from app.repositories.refresh_token_repository import (
    create_refresh_token,
    get_refresh_token_by_hash,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens
)
from app.schemas.auth import RegisterRequest


def register_user(
    db: Session,
    Userdata : RegisterRequest
):

    existing_user = get_user_by_email(
        db,
        Userdata.email
    )

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    role = get_role_by_name(
        db,
        Userdata.role
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "ROLE_NOT_FOUND",
                "message": f"Role '{Userdata.role}' does not exist"
            }
        )

    user = User(
        name=Userdata.name,
        email=Userdata.email,
        password_hash=hash_password(Userdata.password),
        role_id=role.id,
        is_active=True
    )

    return create_user(
        db,
        user
    )


def login_user(
    db: Session,
    email: str,
    password: str
):

    user = get_user_by_email(
        db,
        email
    )

    if not user:

        raise invalid_credentials()

    if not verify_password(
        password,
        user.password_hash
    ):

        raise invalid_credentials()

    if not user.is_active:

        raise inactive_user()

    user.last_login_at = datetime.utcnow()

    update_user(
        db,
        user
    )

    access_token = create_access_token(
        user.id,
        user.role.name
    )

    raw_refresh_token = (
        generate_refresh_token()
    )

    refresh_token = RefreshToken(
        user_id=user.id,

        token_hash=hash_refresh_token(
            raw_refresh_token
        ),

        expires_at=(
            datetime.utcnow()
            +
            timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        ),

        is_revoked=False
    )

    create_refresh_token(
        db,
        refresh_token
    )

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer"
    }


def refresh_access_token(
    db: Session,
    raw_refresh_token: str
):

    token_hash = hash_refresh_token(
        raw_refresh_token
    )

    stored_token = (
        get_refresh_token_by_hash(
            db,
            token_hash
        )
    )

    if not stored_token:

        raise invalid_refresh_token()

    if stored_token.is_revoked:

        raise invalid_refresh_token()

    if (
        stored_token.expires_at
        < datetime.utcnow()
    ):

        raise invalid_refresh_token()

    user = get_user_by_id(
        db,
        stored_token.user_id
    )

    if not user:

        raise invalid_refresh_token()

    if not user.is_active:

        raise inactive_user()

    revoke_refresh_token(
        db,
        stored_token
    )

    access_token = create_access_token(
        user.id,
        user.role.name
    )

    new_raw_refresh_token = (
        generate_refresh_token()
    )

    new_refresh_token = RefreshToken(
        user_id=user.id,

        token_hash=hash_refresh_token(
            new_raw_refresh_token
        ),

        expires_at=(
            datetime.utcnow()
            +
            timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        ),

        is_revoked=False
    )

    create_refresh_token(
        db,
        new_refresh_token
    )

    return {
        "access_token": access_token,
        "refresh_token": new_raw_refresh_token,
        "token_type": "bearer"
    }


def logout_user(
    db: Session,
    raw_refresh_token: str
):

    token_hash = hash_refresh_token(
        raw_refresh_token
    )

    stored_token = (
        get_refresh_token_by_hash(
            db,
            token_hash
        )
    )

    if not stored_token:

        raise invalid_refresh_token()

    if stored_token.is_revoked:

        raise invalid_refresh_token()

    revoke_refresh_token(
        db,
        stored_token
    )

    return {
        "message": "Successfully logged out"
    }


def get_current_user(
    db: Session,
    user_id: int
):

    user = get_user_by_id(
        db,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:

        raise inactive_user()

    return user


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str
):

    if not verify_password(
        current_password,
        user.password_hash
    ):

        raise password_mismatch()

    if current_password == new_password:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "New password must be different "
                "from current password"
            )
        )

    user.password_hash = hash_password(
        new_password
    )

    update_user(
        db,
        user
    )

    revoke_all_user_refresh_tokens(
        db,
        user.id
    )

    return {
        "message": "Password changed successfully"
    }