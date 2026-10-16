from sqlalchemy.orm import Session

from app.models.warehouse_user import WarehouseUser


def get_assignment(
    db: Session,
    warehouse_id: int,
    user_id: int
):
    return (
        db.query(WarehouseUser)
        .filter(
            WarehouseUser.warehouse_id == warehouse_id,
            WarehouseUser.user_id == user_id
        )
        .first()
    )


def get_user_warehouse_assignments(
    db: Session,
    user_id: int
):
    return (
        db.query(WarehouseUser)
        .filter(
            WarehouseUser.user_id == user_id
        )
        .all()
    )


def get_warehouse_users(
    db: Session,
    warehouse_id: int
):
    return (
        db.query(WarehouseUser)
        .filter(
            WarehouseUser.warehouse_id == warehouse_id
        )
        .all()
    )


def create_assignment(
    db: Session,
    assignment: WarehouseUser
):
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment


def delete_assignment(
    db: Session,
    assignment: WarehouseUser
):
    db.delete(assignment)
    db.commit()