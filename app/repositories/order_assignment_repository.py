from sqlalchemy.orm import Session

from app.models.order_assignment import OrderAssignment


def get_assignment_by_id(
    db: Session,
    assignment_id: int
):
    return (
        db.query(OrderAssignment)
        .filter(OrderAssignment.id == assignment_id)
        .first()
    )


def get_order_assignment(
    db: Session,
    order_id: int,
    agent_id: int
):
    return (
        db.query(OrderAssignment)
        .filter(
            OrderAssignment.order_id == order_id,
            OrderAssignment.agent_id == agent_id
        )
        .first()
    )


def get_order_assignments(
    db: Session,
    order_id: int
):
    return (
        db.query(OrderAssignment)
        .filter(OrderAssignment.order_id == order_id)
        .order_by(OrderAssignment.id.desc())
        .all()
    )


def get_agent_assignments(
    db: Session,
    agent_id: int
):
    return (
        db.query(OrderAssignment)
        .filter(OrderAssignment.agent_id == agent_id)
        .order_by(OrderAssignment.id.desc())
        .all()
    )


def create_order_assignment(
    db: Session,
    assignment: OrderAssignment
):
    db.add(assignment)
    db.flush()

    return assignment