from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role_permission import RolePermission


def get_permission_by_name(
    db: Session,
    permission_name: str
):
    return (
        db.query(Permission)
        .filter(
            Permission.name == permission_name
        )
        .first()
    )


def get_role_permission(
    db: Session,
    role_id: int,
    permission_id: int
):
    return (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        )
        .first()
    )


def get_role_permissions(
    db: Session,
    role_id: int
):
    return (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id == role_id
        )
        .all()
    )


def create_permission(
    db: Session,
    permission: Permission
):
    db.add(permission)
    db.commit()
    db.refresh(permission)

    return permission


def create_role_permission(
    db: Session,
    role_permission: RolePermission
):
    db.add(role_permission)
    db.commit()
    db.refresh(role_permission)

    return role_permission