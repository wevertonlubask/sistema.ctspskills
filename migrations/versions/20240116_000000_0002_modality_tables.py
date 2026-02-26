"""Modality tables.

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create modalities table
    op.create_table(
        "modalities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(10), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("min_training_hours", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_modalities_code", "modalities", ["code"])
    op.create_index("ix_modalities_name", "modalities", ["name"])
    op.create_index("ix_modalities_active", "modalities", ["is_active"])

    # Create competences table
    op.create_table(
        "competences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("max_score", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["modality_id"], ["modalities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_competences_modality_id", "competences", ["modality_id"])
    op.create_index(
        "ix_competences_modality_name",
        "competences",
        ["modality_id", "name"],
        unique=True,
    )

    # Create competitors table
    op.create_table(
        "competitors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("document_number", sa.String(20), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("emergency_contact", sa.String(255), nullable=True),
        sa.Column("emergency_phone", sa.String(20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_competitors_user_id", "competitors", ["user_id"])
    op.create_index("ix_competitors_name", "competitors", ["full_name"])
    op.create_index("ix_competitors_active", "competitors", ["is_active"])

    # Create enrollments table (Many-to-Many between Competitor and Modality)
    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competitor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evaluator_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("enrolled_at", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["modality_id"], ["modalities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evaluator_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_enrollments_competitor_id", "enrollments", ["competitor_id"])
    op.create_index("ix_enrollments_modality_id", "enrollments", ["modality_id"])
    op.create_index("ix_enrollments_evaluator_id", "enrollments", ["evaluator_id"])
    op.create_index("ix_enrollments_status", "enrollments", ["status"])
    op.create_index(
        "ix_enrollments_competitor_modality",
        "enrollments",
        ["competitor_id", "modality_id"],
        unique=True,
    )
    op.create_index(
        "ix_enrollments_evaluator_modality",
        "enrollments",
        ["evaluator_id", "modality_id"],
    )


def downgrade() -> None:
    op.drop_table("enrollments")
    op.drop_table("competitors")
    op.drop_table("competences")
    op.drop_table("modalities")
