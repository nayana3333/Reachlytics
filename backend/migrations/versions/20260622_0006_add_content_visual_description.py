"""add content visual description

Revision ID: 20260622_0006
Revises: 20260622_0005
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260622_0006"
down_revision: Union[str, None] = "20260622_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("content_analyses", sa.Column("visual_description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("content_analyses", "visual_description")
