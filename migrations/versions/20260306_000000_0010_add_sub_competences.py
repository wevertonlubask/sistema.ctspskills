"""Add sub_competences table and sub_competence_id to grades.

Revision ID: 0010
Revises: 0009
Create Date: 2026-03-06 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sub_competences table and add sub_competence_id to grades."""
    # Create sub_competences table
    op.create_table(
        "sub_competences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
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
        sa.ForeignKeyConstraint(["competence_id"], ["competences.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sub_competences_competence_id", "sub_competences", ["competence_id"])
    op.create_index(
        "ix_sub_competences_competence_order",
        "sub_competences",
        ["competence_id", "order"],
    )

    # Add sub_competence_id nullable column to grades
    op.add_column(
        "grades",
        sa.Column("sub_competence_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_grades_sub_competence_id",
        "grades",
        "sub_competences",
        ["sub_competence_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_grades_sub_competence_id", "grades", ["sub_competence_id"])

    # Replace the unique constraint to support both modes:
    # - grades without sub-criteria: UNIQUE(exam_id, competitor_id, competence_id) WHERE sub_competence_id IS NULL
    # - grades with sub-criteria:    UNIQUE(exam_id, competitor_id, competence_id, sub_competence_id) WHERE sub_competence_id IS NOT NULL
    op.drop_constraint("uq_grades_exam_competitor_competence", "grades", type_="unique")
    op.execute(
        "CREATE UNIQUE INDEX uq_grades_no_sub "
        "ON grades(exam_id, competitor_id, competence_id) "
        "WHERE sub_competence_id IS NULL"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_grades_with_sub "
        "ON grades(exam_id, competitor_id, competence_id, sub_competence_id) "
        "WHERE sub_competence_id IS NOT NULL"
    )


def downgrade() -> None:
    """Drop sub_competences table and revert grades changes."""
    op.execute("DROP INDEX IF EXISTS uq_grades_with_sub")
    op.execute("DROP INDEX IF EXISTS uq_grades_no_sub")

    op.drop_index("ix_grades_sub_competence_id", table_name="grades")
    op.drop_constraint("fk_grades_sub_competence_id", "grades", type_="foreignkey")
    op.drop_column("grades", "sub_competence_id")

    op.drop_index("ix_sub_competences_competence_order", table_name="sub_competences")
    op.drop_index("ix_sub_competences_competence_id", table_name="sub_competences")
    op.drop_table("sub_competences")

    op.create_unique_constraint(
        "uq_grades_exam_competitor_competence",
        "grades",
        ["exam_id", "competitor_id", "competence_id"],
    )
