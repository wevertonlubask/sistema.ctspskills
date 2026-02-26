"""Evaluator modalities direct assignment table.

Revision ID: 0006
Revises: 0005
Create Date: 2024-01-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create evaluator_modalities table for direct evaluator-modality assignments
    op.create_table(
        "evaluator_modalities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evaluator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["evaluator_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["modality_id"], ["modalities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_evaluator_modalities_evaluator_id",
        "evaluator_modalities",
        ["evaluator_id"],
    )
    op.create_index(
        "ix_evaluator_modalities_modality_id",
        "evaluator_modalities",
        ["modality_id"],
    )
    op.create_index(
        "ix_evaluator_modalities_evaluator_modality",
        "evaluator_modalities",
        ["evaluator_id", "modality_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("evaluator_modalities")
