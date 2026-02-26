"""Platform settings SQLAlchemy model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import GUID, Base
from src.shared.utils.date_utils import utc_now


class PlatformSettingsModel(Base):
    """Platform settings database model (singleton)."""

    __tablename__ = "platform_settings"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    singleton_key: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        default="settings",
    )
    platform_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="SPSkills",
    )
    platform_subtitle: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    browser_title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="SPSkills",
    )
    logo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    logo_collapsed_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    favicon_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    primary_color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("singleton_key = 'settings'", name="ck_platform_settings_singleton"),
        Index("ix_platform_settings_singleton", "singleton_key", unique=True),
    )
