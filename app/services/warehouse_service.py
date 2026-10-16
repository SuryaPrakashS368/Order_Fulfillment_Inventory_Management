from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.constants import Roles

from app.models.warehouse import Warehouse
from app.models.warehouse_user import WarehouseUser

from app.repositories.warehouse_repository import (
    get_warehouse_by_id,
    get_warehouse_by_name,
    get_all_warehouses,
    create_warehouse,
    update_warehouse
)

from app.repositories.warehouse_user_repository import (
    get_assignment,
    get_warehouse_users,
    create_assignment,
    delete_assignment
)

from app.repositories.user_repository import (
    get_user_by_id
)


def create_warehouse_service(
    db: Session,
    name: str,
    location: str,
    capacity: int
):

    existing = get_warehouse_by_name(
        db,
        name
    )

    if existing:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Warehouse already exists"
        )

    warehouse = Warehouse(
        name=name,
        location=location,
        capacity=capacity,
        is_active=True
    )

    return create_warehouse(
        db,
        warehouse
    )


def list_warehouses(
    db: Session
):

    return get_all_warehouses(db)


def get_warehouse(
    db: Session,
    warehouse_id: int
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

    return warehouse


def update_warehouse_service(
    db: Session,
    warehouse_id: int,
    name: str | None,
    location: str | None,
    capacity: int | None
):

    warehouse = get_warehouse(
        db,
        warehouse_id
    )

    if name and name != warehouse.name:

        existing = get_warehouse_by_name(
            db,
            name
        )

        if existing:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Warehouse already exists"
            )

        warehouse.name = name

    if location is not None:

        warehouse.location = location

    if capacity is not None:

        warehouse.capacity = capacity

    return update_warehouse(
        db,
        warehouse
    )


def update_warehouse_status(
    db: Session,
    warehouse_id: int,
    is_active: bool
):

    warehouse = get_warehouse(
        db,
        warehouse_id
    )

    warehouse.is_active = is_active

    return update_warehouse(
        db,
        warehouse
    )


def assign_user_to_warehouse(
    db: Session,
    warehouse_id: int,
    user_id: int
):

    warehouse = get_warehouse(
        db,
        warehouse_id
    )

    if not warehouse.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign user to inactive warehouse"
        )

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

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign inactive user"
        )

    allowed_roles = [
        Roles.WAREHOUSE_MANAGER,
        Roles.FULFILLMENT_AGENT
    ]

    if user.role.name not in allowed_roles:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only Warehouse Manager or "
                "Fulfillment Agent can be "
                "assigned to a warehouse"
            )
        )

    existing = get_assignment(
        db,
        warehouse_id,
        user_id
    )

    if existing:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already assigned to warehouse"
        )

    assignment = WarehouseUser(
        warehouse_id=warehouse_id,
        user_id=user_id
    )

    return create_assignment(
        db,
        assignment
    )


def remove_user_from_warehouse(
    db: Session,
    warehouse_id: int,
    user_id: int
):

    assignment = get_assignment(
        db,
        warehouse_id,
        user_id
    )

    if not assignment:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse assignment not found"
        )

    delete_assignment(
        db,
        assignment
    )

    return {
        "message": "User removed from warehouse"
    }


def list_warehouse_users(
    db: Session,
    warehouse_id: int
):

    assignments = get_warehouse_users(
        db,
        warehouse_id
    )

    result = []

    for assignment in assignments:

        user = assignment.user

        result.append(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.name,
                "is_active": user.is_active
            }
        )

    return result