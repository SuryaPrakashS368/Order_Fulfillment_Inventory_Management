from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.models.order import OrderStatus
from app.models.order_assignment import OrderAssignment

from app.repositories.order_repository import (
    get_order_by_id
)

from app.repositories.order_assignment_repository import (
    get_order_assignment,
    get_order_assignments,
    get_agent_assignments,
    create_order_assignment
)

from app.repositories.user_repository import (
    get_user_by_id
)

from app.repositories.warehouse_user_repository import (
    get_assignment as get_warehouse_assignment
)


def assign_fulfillment_agent_service(
    db: Session,
    order_id: int,
    agent_id: int,
    assigned_by: int,
    assigned_by_role: str
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if assigned_by_role not in {
        Roles.ADMIN,
        Roles.WAREHOUSE_MANAGER
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot assign fulfillment agents"
        )

    if order.status not in {
        OrderStatus.CONFIRMED,
        OrderStatus.PROCESSING
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Agents can only be assigned to "
                "confirmed or processing orders"
            )
        )

    if (
        assigned_by_role == Roles.WAREHOUSE_MANAGER
        and not get_warehouse_assignment(
            db,
            order.warehouse_id,
            assigned_by
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this warehouse"
        )

    agent = get_user_by_id(db, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fulfillment agent not found"
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The fulfillment agent is inactive"
        )

    if agent.role.name != Roles.FULFILLMENT_AGENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected user is not a fulfillment agent"
        )

    warehouse_assignment = get_warehouse_assignment(
        db,
        order.warehouse_id,
        agent.id
    )

    if not warehouse_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The fulfillment agent must be assigned "
                "to the order's warehouse first"
            )
        )

    existing = get_order_assignment(
        db,
        order_id,
        agent_id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This agent is already assigned to the order"
        )

    assignment = OrderAssignment(
        order_id=order_id,
        agent_id=agent_id,
        assigned_by=assigned_by
    )

    try:
        create_order_assignment(db, assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    except Exception:
        db.rollback()
        raise


def get_order_assignments_service(
    db: Session,
    order_id: int
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return get_order_assignments(db, order_id)


def get_my_fulfillment_assignments_service(
    db: Session,
    agent_id: int
):
    return get_agent_assignments(db, agent_id)