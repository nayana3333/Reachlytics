"""add report ml verdict prediction

Revision ID: 20260622_0005
Revises: 20260621_0004
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260622_0005"
down_revision: Union[str, None] = "20260621_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("reports", sa.Column("ml_verdict_prediction", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("reports", "ml_verdict_prediction")
