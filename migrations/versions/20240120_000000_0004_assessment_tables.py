"""Create assessment tables.

Revision ID: 0004
Revises: 0003
Create Date: 2024-01-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create assessment tables: exams, exam_competences, grades, grade_audit_logs."""
    # Create exams table
    op.create_table(
        "exams",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assessment_type", sa.String(20), nullable=False),
        sa.Column("exam_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.ForeignKeyConstraint(["modality_id"], ["modalities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for exams
    op.create_index("ix_exams_modality_id", "exams", ["modality_id"])
    op.create_index("ix_exams_assessment_type", "exams", ["assessment_type"])
    op.create_index("ix_exams_exam_date", "exams", ["exam_date"])
    op.create_index("ix_exams_created_by", "exams", ["created_by"])
    op.create_index("ix_exams_modality_date", "exams", ["modality_id", "exam_date"])
    op.create_index("ix_exams_active", "exams", ["is_active"])
    op.create_index("ix_exams_type_date", "exams", ["assessment_type", "exam_date"])

    # Create exam_competences association table
    op.create_table(
        "exam_competences",
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["competence_id"], ["competences.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("exam_id", "competence_id"),
    )

    # Create grades table
    op.create_table(
        "grades",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competitor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.ForeignKeyConstraint(["competence_id"], ["competences.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "exam_id", "competitor_id", "competence_id", name="uq_grades_exam_competitor_competence"
        ),
    )

    # Create indexes for grades
    op.create_index("ix_grades_exam_id", "grades", ["exam_id"])
    op.create_index("ix_grades_competitor_id", "grades", ["competitor_id"])
    op.create_index("ix_grades_competence_id", "grades", ["competence_id"])
    op.create_index("ix_grades_created_by", "grades", ["created_by"])
    op.create_index("ix_grades_updated_by", "grades", ["updated_by"])
    op.create_index("ix_grades_exam_competitor", "grades", ["exam_id", "competitor_id"])
    op.create_index("ix_grades_exam_competence", "grades", ["exam_id", "competence_id"])
    op.create_index("ix_grades_competitor_competence", "grades", ["competitor_id", "competence_id"])

    # Create grade_audit_logs table
    op.create_table(
        "grade_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("grade_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("old_score", sa.Float(), nullable=True),
        sa.Column("new_score", sa.Float(), nullable=True),
        sa.Column("old_notes", sa.Text(), nullable=True),
        sa.Column("new_notes", sa.Text(), nullable=True),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["grade_id"], ["grades.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for grade_audit_logs
    op.create_index("ix_grade_audit_logs_grade_id", "grade_audit_logs", ["grade_id"])
    op.create_index("ix_grade_audit_logs_action", "grade_audit_logs", ["action"])
    op.create_index("ix_grade_audit_logs_changed_by", "grade_audit_logs", ["changed_by"])
    op.create_index("ix_grade_audit_logs_changed_at", "grade_audit_logs", ["changed_at"])
    op.create_index("ix_audit_grade_time", "grade_audit_logs", ["grade_id", "changed_at"])
    op.create_index("ix_audit_user_time", "grade_audit_logs", ["changed_by", "changed_at"])


def downgrade() -> None:
    """Drop assessment tables."""
    # Drop grade_audit_logs table first (depends on grades)
    op.drop_index("ix_audit_user_time", table_name="grade_audit_logs")
    op.drop_index("ix_audit_grade_time", table_name="grade_audit_logs")
    op.drop_index("ix_grade_audit_logs_changed_at", table_name="grade_audit_logs")
    op.drop_index("ix_grade_audit_logs_changed_by", table_name="grade_audit_logs")
    op.drop_index("ix_grade_audit_logs_action", table_name="grade_audit_logs")
    op.drop_index("ix_grade_audit_logs_grade_id", table_name="grade_audit_logs")
    op.drop_table("grade_audit_logs")

    # Drop grades table (depends on exams)
    op.drop_index("ix_grades_competitor_competence", table_name="grades")
    op.drop_index("ix_grades_exam_competence", table_name="grades")
    op.drop_index("ix_grades_exam_competitor", table_name="grades")
    op.drop_index("ix_grades_updated_by", table_name="grades")
    op.drop_index("ix_grades_created_by", table_name="grades")
    op.drop_index("ix_grades_competence_id", table_name="grades")
    op.drop_index("ix_grades_competitor_id", table_name="grades")
    op.drop_index("ix_grades_exam_id", table_name="grades")
    op.drop_table("grades")

    # Drop exam_competences association table
    op.drop_table("exam_competences")

    # Drop exams table
    op.drop_index("ix_exams_type_date", table_name="exams")
    op.drop_index("ix_exams_active", table_name="exams")
    op.drop_index("ix_exams_modality_date", table_name="exams")
    op.drop_index("ix_exams_created_by", table_name="exams")
    op.drop_index("ix_exams_exam_date", table_name="exams")
    op.drop_index("ix_exams_assessment_type", table_name="exams")
    op.drop_index("ix_exams_modality_id", table_name="exams")
    op.drop_table("exams")
