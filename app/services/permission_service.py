from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.permission import Permission

from app.core.permission_config import (
    ROLE_PERMISSIONS,
)


def configure_permissions(db: Session):

    try:
        for role_name, permission_names in (
            ROLE_PERMISSIONS.items()
        ):

            # Find the role
            role = (
                db.query(Role)
                .filter(
                    Role.name == role_name
                )
                .first()
            )

            if role is None:
                print(
                    f"Role not found: {role_name}"
                )
                continue

            # Existing permission IDs for this role
            existing_permission_ids = {
                permission.id
                for permission in role.permissions
            }

            for permission_name in permission_names:

                # Find the permission
                permission = (
                    db.query(Permission)
                    .filter(
                        Permission.name
                        == permission_name
                    )
                    .first()
                )

                # Create missing permission
                if permission is None:

                    permission = Permission(
                        name=permission_name,
                        description=(
                            f"Allows {permission_name}"
                        ),
                    )

                    db.add(permission)
                    db.flush()

                # Assign permission to role
                if (
                    permission.id
                    not in existing_permission_ids
                ):
                    role.permissions.append(
                        permission
                    )

                    existing_permission_ids.add(
                        permission.id
                    )

        db.commit()

        print(
            "Permissions configured successfully."
        )

    except Exception:
        db.rollback()
        raise
