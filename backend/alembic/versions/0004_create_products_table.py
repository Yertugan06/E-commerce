"""create products table and add FK from cart_items/order_items product_id

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        "DELETE FROM cart_items WHERE product_id NOT IN (SELECT id FROM products)"
    )
    op.execute(
        "DELETE FROM order_items WHERE product_id NOT IN (SELECT id FROM products)"
    )

    op.create_foreign_key(
        "fk_cart_items_product_id",
        "cart_items", "products",
        ["product_id"], ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_order_items_product_id",
        "order_items", "products",
        ["product_id"], ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_cart_items_product_id", "cart_items", type_="foreignkey")
    op.drop_constraint("fk_order_items_product_id", "order_items", type_="foreignkey")
    op.drop_table("products")
