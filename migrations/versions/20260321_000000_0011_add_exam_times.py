"""Add time_limit_minutes to exams and exam_competitor_times table.

Revision ID: 0011
Revises: 0010
Create Date: 2026-03-21 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add time_limit_minutes to exams and create exam_competitor_times table."""
    # Add time_limit_minutes to exams
    op.add_column(
        "exams",
        sa.Column("time_limit_minutes", sa.Integer(), nullable=True),
    )

    # Create exam_competitor_times table
    op.create_table(
        "exam_competitor_times",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competitor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exam_id", "competitor_id", name="uq_exam_competitor_time"),
    )
    op.create_index("ix_exam_competitor_times_exam_id", "exam_competitor_times", ["exam_id"])
    op.create_index("ix_exam_competitor_times_competitor_id", "exam_competitor_times", ["competitor_id"])


def downgrade() -> None:
    """Reverse the migration."""
    op.drop_table("exam_competitor_times")
    op.drop_column("exams", "time_limit_minutes")
