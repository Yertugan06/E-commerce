"""add unique constraint on cart_items(cart_id, product_id)

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-20

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DELETE FROM cart_items WHERE ctid NOT IN ("
        "SELECT min(ctid) FROM cart_items GROUP BY cart_id, product_id"
        ")"
    )
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_cart_item_product') THEN
                ALTER TABLE cart_items ADD CONSTRAINT uq_cart_item_product UNIQUE (cart_id, product_id);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute(
        "ALTER TABLE cart_items DROP CONSTRAINT IF EXISTS uq_cart_item_product"
    )
