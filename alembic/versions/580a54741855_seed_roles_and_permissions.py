"""seed roles and permissions

Revision ID: 580a54741855
Revises: 060141c8bdb8
Create Date: 2026-10-08 11:13:08.261905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '580a54741855'
down_revision: Union[str, Sequence[str], None] = '060141c8bdb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
