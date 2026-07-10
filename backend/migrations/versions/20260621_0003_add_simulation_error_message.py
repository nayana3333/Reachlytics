"""add simulation error message

Revision ID: 20260621_0003
Revises: 20260621_0002
Create Date: 2026-06-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260621_0003"
down_revision: Union[str, None] = "20260621_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("simulations", sa.Column("error_message", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("simulations", "error_message")
