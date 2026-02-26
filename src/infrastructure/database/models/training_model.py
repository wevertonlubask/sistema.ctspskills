"""Training-related SQLAlchemy models."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import GUID, Base
from src.shared.utils.date_utils import utc_now


class TrainingSessionModel(Base):
    """Training session database model."""

    __tablename__ = "training_sessions"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    competitor_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    modality_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("modalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enrollment_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    training_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hours: Mapped[float] = mapped_column(Float, nullable=False)
    training_type: Mapped[str] = mapped_column(
        String(20),
        default="senai",
        nullable=False,
        index=True,
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )
    validated_by: Mapped[UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    validated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    # Relationships
    competitor: Mapped["CompetitorModel"] = relationship(
        "CompetitorModel",
        backref="training_sessions",
    )
    modality: Mapped["ModalityModel"] = relationship(
        "ModalityModel",
        back_populates="training_sessions",
    )
    enrollment: Mapped["EnrollmentModel"] = relationship(
        "EnrollmentModel",
        backref="training_sessions",
    )
    validator: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[validated_by],
    )
    evidences: Mapped[list["EvidenceModel"]] = relationship(
        "EvidenceModel",
        back_populates="training_session",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_training_competitor_date", "competitor_id", "training_date"),
        Index("ix_training_competitor_modality", "competitor_id", "modality_id"),
        Index("ix_training_status_date", "status", "training_date"),
        Index("ix_training_validator", "validated_by", "status"),
    )


class TrainingTypeConfigModel(Base):
    """Training type configuration database model."""

    __tablename__ = "training_type_configs"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
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

    __table_args__ = (Index("ix_training_type_configs_active", "is_active", "display_order"),)


class EvidenceModel(Base):
    """Evidence database model for training documentation."""

    __tablename__ = "evidences"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    training_session_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence_type: Mapped[str] = mapped_column(
        String(20),
        default="photo",
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
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

    # Relationships
    training_session: Mapped[TrainingSessionModel] = relationship(
        "TrainingSessionModel",
        back_populates="evidences",
    )
    uploader: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[uploaded_by],
    )

    __table_args__ = (Index("ix_evidences_training_type", "training_session_id", "evidence_type"),)


# Import related models for relationships
from src.infrastructure.database.models.modality_model import (  # noqa: E402
    CompetitorModel,
    EnrollmentModel,
    ModalityModel,
)
from src.infrastructure.database.models.user_model import UserModel  # noqa: E402
