"""Create platform_settings table.

Revision ID: 0008
Revises: 0007
Create Date: 2024-01-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create platform_settings table."""
    op.create_table(
        "platform_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "singleton_key", sa.String(10), unique=True, nullable=False, server_default="settings"
        ),
        sa.Column("platform_name", sa.String(100), nullable=False, server_default="SPSkills"),
        sa.Column("platform_subtitle", sa.String(200), nullable=True),
        sa.Column("browser_title", sa.String(100), nullable=False, server_default="SPSkills"),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("logo_collapsed_url", sa.String(500), nullable=True),
        sa.Column("favicon_url", sa.String(500), nullable=True),
        sa.Column("primary_color", sa.String(7), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("singleton_key = 'settings'", name="ck_platform_settings_singleton"),
    )

    # Create unique index on singleton_key
    op.create_index(
        "ix_platform_settings_singleton", "platform_settings", ["singleton_key"], unique=True
    )


def downgrade() -> None:
    """Drop platform_settings table."""
    op.drop_index("ix_platform_settings_singleton", table_name="platform_settings")
    op.drop_table("platform_settings")
