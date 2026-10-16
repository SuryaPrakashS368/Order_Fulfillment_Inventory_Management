from datetime import datetime

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def create_refresh_token(
    db: Session,
    refresh_token: RefreshToken
):

    db.add(refresh_token)

    db.commit()

    db.refresh(refresh_token)

    return refresh_token


def get_refresh_token_by_hash(
    db: Session,
    token_hash: str
):

    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash
        )
        .first()
    )


def revoke_refresh_token(
    db: Session,
    refresh_token: RefreshToken
):

    refresh_token.is_revoked = True

    refresh_token.revoked_at = datetime.utcnow()

    db.commit()

    db.refresh(refresh_token)

    return refresh_token


def revoke_all_user_refresh_tokens(
    db: Session,
    user_id: int
):

    tokens = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        )
        .all()
    )

    now = datetime.utcnow()

    for token in tokens:

        token.is_revoked = True

        token.revoked_at = now

    db.commit()

    return tokens