from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str
):

    return (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


def get_user_by_id(
    db: Session,
    user_id: int
):

    return (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

def get_role_by_name(
    db: Session,
    role_name: str
):
    return (
        db.query(Role)
        .filter(Role.name == role_name)
        .first()
    )
def get_users(
    db: Session
):
    return (
        db.query(User)
        .order_by(User.id)
        .all()
    )

def create_user(
    db: Session,
    user: User
):

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def update_user(
    db: Session,
    user: User
):

    db.commit()

    db.refresh(user)

    return user