from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.core.security import hash_password

from app.models.user import User

from app.repositories.user_repository import (
    get_user_by_email,
    get_user_by_id,
    get_users,
    create_user,
    update_user
)

from app.repositories.user_repository import (
    get_role_by_name
)
from app.schemas.user import AdminCreateUserRequest


def create_user_by_admin(
    db: Session,
    Userdata : AdminCreateUserRequest
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
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


def list_users(
    db: Session
):
    return get_users(db)


def get_user(
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

    return user


def update_user_details(
    db: Session,
    user_id: int,
    name: str | None,
    email: str | None
):

    user = get_user(
        db,
        user_id
    )

    if email and email != user.email:

        existing_user = get_user_by_email(
            db,
            email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        user.email = email

    if name is not None:
        user.name = name

    return update_user(
        db,
        user
    )


def update_user_status(
    db: Session,
    user_id: int,
    is_active: bool
):

    user = get_user(
        db,
        user_id
    )

    user.is_active = is_active

    return update_user(
        db,
        user
    )