"""add simulation progress stage

Revision ID: 20260621_0002
Revises: 20260621_0001
Create Date: 2026-06-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260621_0002"
down_revision: Union[str, None] = "20260621_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column("progress_stage", sa.String(length=80), nullable=False, server_default="queued"),
    )


def downgrade() -> None:
    op.drop_column("simulations", "progress_stage")
