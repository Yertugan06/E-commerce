"""protect order_items from product cascade, add product_name

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_NAME = "fk_order_items_product_id"


def _fk_exists() -> str | None:
    conn = op.get_bind()
    return conn.execute(
        sa.text(
            "SELECT conname FROM pg_constraint "
            "WHERE conrelid = 'order_items'::regclass "
            "AND contype = 'f' "
            "AND confrelid = 'products'::regclass"
        )
    ).scalar()


def _column_exists(name: str) -> bool:
    conn = op.get_bind()
    return conn.execute(
        sa.text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'order_items' AND column_name = :name"
        ).bindparams(name=name)
    ).scalar() is not None


def upgrade() -> None:
    existing = _fk_exists()
    if existing:
        op.drop_constraint(existing, "order_items", type_="foreignkey")
    op.create_foreign_key(
        FK_NAME,
        "order_items", "products",
        ["product_id"], ["id"],
        ondelete="RESTRICT",
    )
    if not _column_exists("product_name"):
        op.add_column(
            "order_items",
            sa.Column("product_name", sa.String(), nullable=False, server_default=""),
        )


def downgrade() -> None:
    if _column_exists("product_name"):
        op.drop_column("order_items", "product_name")
    existing = _fk_exists()
    if existing:
        op.drop_constraint(existing, "order_items", type_="foreignkey")
    op.create_foreign_key(
        FK_NAME,
        "order_items", "products",
        ["product_id"], ["id"],
        ondelete="CASCADE",
    )
