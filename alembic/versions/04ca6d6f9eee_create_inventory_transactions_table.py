
"""create inventory transactions table

Revision ID: 04ca6d6f9eee
Revises: 86b45ff2770d
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "04ca6d6f9eee"
down_revision: Union[str, Sequence[str], None] = "86b45ff2770d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Existing PostgreSQL enum types: reuse them.
order_from_status_enum = postgresql.ENUM(
    "PENDING",
    "CONFIRMED",
    "PROCESSING",
    "PACKED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "FAILED",
    "RETURNED",
    name="order_history_from_status",
    create_type=False,
)

order_to_status_enum = postgresql.ENUM(
    "PENDING",
    "CONFIRMED",
    "PROCESSING",
    "PACKED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "FAILED",
    "RETURNED",
    name="order_history_to_status",
    create_type=False,
)

# This enum is missing, so this migration creates it.
inventory_transaction_enum = postgresql.ENUM(
    "PURCHASE",
    "SALE",
    "RESERVATION",
    "RELEASE",
    "ADJUSTMENT",
    "TRANSFER_IN",
    "TRANSFER_OUT",
    "RETURN",
    "DAMAGE",
    name="inventory_transaction_type",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()

    # Create only if it does not already exist.
    inventory_transaction_enum.create(
        bind,
        checkfirst=True,
    )

    # Inventory transactions
    op.create_table(
        "inventory_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_type",
            inventory_transaction_enum,
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reference_entity", sa.String(100), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("transaction_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )

    op.create_index(
        "ix_inventory_transactions_product_id",
        "inventory_transactions",
        ["product_id"],
    )
    op.create_index(
        "ix_inventory_transactions_transaction_type",
        "inventory_transactions",
        ["transaction_type"],
    )
    op.create_index(
        "ix_inventory_transactions_user_id",
        "inventory_transactions",
        ["user_id"],
    )
    op.create_index(
        "ix_inventory_transactions_warehouse_id",
        "inventory_transactions",
        ["warehouse_id"],
    )

    # Warehouse-user assignments
    op.create_table(
        "warehouse_users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.UniqueConstraint(
            "warehouse_id",
            "user_id",
            name="uq_warehouse_user",
        ),
    )

    op.create_index(
        "ix_warehouse_users_user_id",
        "warehouse_users",
        ["user_id"],
    )
    op.create_index(
        "ix_warehouse_users_warehouse_id",
        "warehouse_users",
        ["warehouse_id"],
    )

    # Order status history: reuse existing enum types.
    op.create_table(
        "order_status_history",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column(
            "from_status",
            order_from_status_enum,
            nullable=True,
        ),
        sa.Column(
            "to_status",
            order_to_status_enum,
            nullable=False,
        ),
        sa.Column("changed_by", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
    )

    op.create_index(
        "ix_order_status_history_changed_by",
        "order_status_history",
        ["changed_by"],
    )
    op.create_index(
        "ix_order_status_history_order_id",
        "order_status_history",
        ["order_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_order_status_history_order_id",
        table_name="order_status_history",
    )
    op.drop_index(
        "ix_order_status_history_changed_by",
        table_name="order_status_history",
    )
    op.drop_table("order_status_history")

    op.drop_index(
        "ix_warehouse_users_warehouse_id",
        table_name="warehouse_users",
    )
    op.drop_index(
        "ix_warehouse_users_user_id",
        table_name="warehouse_users",
    )
    op.drop_table("warehouse_users")

    op.drop_index(
        "ix_inventory_transactions_warehouse_id",
        table_name="inventory_transactions",
    )
    op.drop_index(
        "ix_inventory_transactions_user_id",
        table_name="inventory_transactions",
    )
    op.drop_index(
        "ix_inventory_transactions_transaction_type",
        table_name="inventory_transactions",
    )
    op.drop_index(
        "ix_inventory_transactions_product_id",
        table_name="inventory_transactions",
    )
    op.drop_table("inventory_transactions")

    # This migration creates this enum; the two order enums are preserved.
    inventory_transaction_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )
