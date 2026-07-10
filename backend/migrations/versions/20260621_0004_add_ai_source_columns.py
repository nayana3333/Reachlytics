"""add ai source columns

Revision ID: 20260621_0004
Revises: 20260621_0003
Create Date: 2026-06-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260621_0004"
down_revision: Union[str, None] = "20260621_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transcripts",
        sa.Column("ai_source", sa.String(length=20), nullable=False, server_default="fallback"),
    )
    op.add_column(
        "content_analyses",
        sa.Column("ai_source", sa.String(length=20), nullable=False, server_default="fallback"),
    )
    op.add_column(
        "simulations",
        sa.Column("personas_ai_source", sa.String(length=20), nullable=False, server_default="fallback"),
    )
    op.add_column(
        "simulations",
        sa.Column("reasons_ai_source", sa.String(length=20), nullable=False, server_default="fallback"),
    )


def downgrade() -> None:
    op.drop_column("simulations", "reasons_ai_source")
    op.drop_column("simulations", "personas_ai_source")
    op.drop_column("content_analyses", "ai_source")
    op.drop_column("transcripts", "ai_source")
