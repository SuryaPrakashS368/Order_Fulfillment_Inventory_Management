from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission

from app.routes.auth import get_current_user


def require_permission(permission_name: str):

    def permission_checker(
        current_user: User = Depends(
            get_current_user
        ),
        db: Session = Depends(get_db),
    ):

        # 1. Check whether the user is active
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # 2. Check whether the user has a role
        if current_user.role_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role is not assigned",
            )

        # 3. Find the configured permission
        permission = (
            db.query(Permission)
            .filter(
                Permission.name == permission_name
            )
            .first()
        )

        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Permission '{permission_name}' "
                    "is not configured"
                ),
            )

        # 4. Check the role-permission mapping
        role_permission = (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id
                == current_user.role_id,
                RolePermission.permission_id
                == permission.id,
            )
            .first()
        )

        if role_permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission",
            )

        # 5. Return authenticated user
        return current_user

    return permission_checker