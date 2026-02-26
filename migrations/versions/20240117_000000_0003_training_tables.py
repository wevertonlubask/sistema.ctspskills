"""Create training tables.

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create training_sessions and evidences tables."""
    # Create training_sessions table
    op.create_table(
        "training_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competitor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enrollment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("training_date", sa.Date(), nullable=False),
        sa.Column("hours", sa.Float(), nullable=False),
        sa.Column("training_type", sa.String(20), nullable=False, server_default="senai"),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("validated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["modality_id"], ["modalities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["enrollment_id"], ["enrollments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["validated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for training_sessions
    op.create_index("ix_training_sessions_competitor_id", "training_sessions", ["competitor_id"])
    op.create_index("ix_training_sessions_modality_id", "training_sessions", ["modality_id"])
    op.create_index("ix_training_sessions_enrollment_id", "training_sessions", ["enrollment_id"])
    op.create_index("ix_training_sessions_training_date", "training_sessions", ["training_date"])
    op.create_index("ix_training_sessions_status", "training_sessions", ["status"])
    op.create_index("ix_training_sessions_training_type", "training_sessions", ["training_type"])
    op.create_index("ix_training_sessions_validated_by", "training_sessions", ["validated_by"])
    op.create_index(
        "ix_training_competitor_date", "training_sessions", ["competitor_id", "training_date"]
    )
    op.create_index(
        "ix_training_competitor_modality", "training_sessions", ["competitor_id", "modality_id"]
    )
    op.create_index("ix_training_status_date", "training_sessions", ["status", "training_date"])
    op.create_index("ix_training_validator", "training_sessions", ["validated_by", "status"])

    # Create evidences table
    op.create_table(
        "evidences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("training_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("evidence_type", sa.String(20), nullable=False, server_default="photo"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["training_session_id"], ["training_sessions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for evidences
    op.create_index("ix_evidences_training_session_id", "evidences", ["training_session_id"])
    op.create_index("ix_evidences_uploaded_by", "evidences", ["uploaded_by"])
    op.create_index(
        "ix_evidences_training_type", "evidences", ["training_session_id", "evidence_type"]
    )


def downgrade() -> None:
    """Drop training tables."""
    # Drop evidences table first (depends on training_sessions)
    op.drop_index("ix_evidences_training_type", table_name="evidences")
    op.drop_index("ix_evidences_uploaded_by", table_name="evidences")
    op.drop_index("ix_evidences_training_session_id", table_name="evidences")
    op.drop_table("evidences")

    # Drop training_sessions table
    op.drop_index("ix_training_validator", table_name="training_sessions")
    op.drop_index("ix_training_status_date", table_name="training_sessions")
    op.drop_index("ix_training_competitor_modality", table_name="training_sessions")
    op.drop_index("ix_training_competitor_date", table_name="training_sessions")
    op.drop_index("ix_training_sessions_validated_by", table_name="training_sessions")
    op.drop_index("ix_training_sessions_training_type", table_name="training_sessions")
    op.drop_index("ix_training_sessions_status", table_name="training_sessions")
    op.drop_index("ix_training_sessions_training_date", table_name="training_sessions")
    op.drop_index("ix_training_sessions_enrollment_id", table_name="training_sessions")
    op.drop_index("ix_training_sessions_modality_id", table_name="training_sessions")
    op.drop_index("ix_training_sessions_competitor_id", table_name="training_sessions")
    op.drop_table("training_sessions")
