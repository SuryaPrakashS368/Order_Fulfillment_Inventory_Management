from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles

from app.repositories.dashboard_repository import (
    get_total_orders,
    get_orders_by_status,
    get_total_products,
    get_inventory_summary,
    get_low_stock_inventory,
    get_user_warehouse_ids,
    get_agent_assignment_summary,
)


def get_dashboard_summary_service(
    db: Session,
    current_user,
):
    role_name = current_user.role.name

    if role_name == Roles.ADMIN:
        warehouse_ids = None

    elif role_name == Roles.WAREHOUSE_MANAGER:
        warehouse_ids = get_user_warehouse_ids(
            db,
            current_user.id,
        )

    elif role_name == Roles.FULFILLMENT_AGENT:
        return {
            "role": role_name,
            "active_assignments": (
                get_agent_assignment_summary(
                    db,
                    current_user.id,
                )
            ),
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this dashboard",
        )

    return {
        "role": role_name,
        "total_orders": get_total_orders(
            db,
            warehouse_ids,
        ),
        "orders_by_status": get_orders_by_status(
            db,
            warehouse_ids,
        ),
        "total_products": get_total_products(db),
        "inventory": get_inventory_summary(
            db,
            warehouse_ids,
        ),
    }


def get_low_stock_service(
    db: Session,
    current_user,
    skip: int = 0,
    limit: int = 20,
):
    role_name = current_user.role.name

    if role_name == Roles.ADMIN:
        warehouse_ids = None

    elif role_name == Roles.WAREHOUSE_MANAGER:
        warehouse_ids = get_user_warehouse_ids(
            db,
            current_user.id,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access low-stock reports",
        )

    # No assigned warehouses means no accessible inventory.
    if warehouse_ids is not None and not warehouse_ids:
        return []

    return get_low_stock_inventory(
        db=db,
        warehouse_ids=warehouse_ids,
        skip=skip,
        limit=limit,
    )