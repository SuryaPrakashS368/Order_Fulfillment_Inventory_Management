from fastapi import (
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.constants import Roles

from app.core.database import get_db

from app.dependencies.auth import (
    get_current_user
)

from app.repositories.warehouse_repository import (
    get_warehouse_by_id
)

from app.repositories.warehouse_user_repository import (
    get_assignment
)


def get_current_warehouse(
    warehouse_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    warehouse = get_warehouse_by_id(
        db,
        warehouse_id
    )

    if not warehouse:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    if not warehouse.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warehouse is inactive"
        )

    # Admin can access every warehouse
    if current_user.role.name == Roles.ADMIN:

        return warehouse

    assignment = get_assignment(
        db,
        warehouse_id,
        current_user.id
    )

    if not assignment:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to this warehouse"
        )

    return warehouse