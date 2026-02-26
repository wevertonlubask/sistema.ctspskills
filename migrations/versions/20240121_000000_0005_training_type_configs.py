"""Training type configs table.

Revision ID: 0005
Revises: 0004
Create Date: 2024-01-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create training_type_configs table
    op.create_table(
        "training_type_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_training_type_configs_code", "training_type_configs", ["code"])
    op.create_index(
        "ix_training_type_configs_active",
        "training_type_configs",
        ["is_active", "display_order"],
    )

    # Insert default training types (SENAI and FORA)
    op.execute(
        """
        INSERT INTO training_type_configs (id, code, name, description, is_active, display_order, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'senai', 'SENAI', 'Treinamento realizado nas dependências do SENAI', true, 1, NOW(), NOW()),
            (gen_random_uuid(), 'external', 'FORA', 'Treinamento realizado fora do SENAI', true, 2, NOW(), NOW())
    """
    )


def downgrade() -> None:
    op.drop_table("training_type_configs")
