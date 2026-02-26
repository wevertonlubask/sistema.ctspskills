"""Modality-related SQLAlchemy models."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
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
from src.infrastructure.database.types import EncryptedString
from src.shared.utils.date_utils import utc_now

if TYPE_CHECKING:
    from src.infrastructure.database.models.assessment_model import ExamModel
    from src.infrastructure.database.models.training_model import TrainingSessionModel


class ModalityModel(Base):
    """Modality database model."""

    __tablename__ = "modalities"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_training_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
    competences: Mapped[list[CompetenceModel]] = relationship(
        "CompetenceModel",
        back_populates="modality",
        cascade="all, delete-orphan",
    )
    enrollments: Mapped[list[EnrollmentModel]] = relationship(
        "EnrollmentModel",
        back_populates="modality",
        cascade="all, delete-orphan",
    )
    exams: Mapped[list[ExamModel]] = relationship(
        "ExamModel",
        back_populates="modality",
        cascade="all, delete-orphan",
    )
    training_sessions: Mapped[list[TrainingSessionModel]] = relationship(
        "TrainingSessionModel",
        back_populates="modality",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_modalities_name", "name"),
        Index("ix_modalities_active", "is_active"),
    )


class CompetenceModel(Base):
    """Competence database model."""

    __tablename__ = "competences"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    modality_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("modalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    modality: Mapped[ModalityModel] = relationship(
        "ModalityModel",
        back_populates="competences",
    )

    __table_args__ = (Index("ix_competences_modality_name", "modality_id", "name", unique=True),)


class CompetitorModel(Base):
    """Competitor database model."""

    __tablename__ = "competitors"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_number: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    phone: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    emergency_phone: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    user: Mapped[UserModel] = relationship("UserModel", backref="competitor")
    enrollments: Mapped[list[EnrollmentModel]] = relationship(
        "EnrollmentModel",
        back_populates="competitor",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_competitors_name", "full_name"),
        Index("ix_competitors_active", "is_active"),
    )


class EnrollmentModel(Base):
    """Enrollment database model - Many-to-Many between Competitor and Modality."""

    __tablename__ = "enrollments"

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
    evaluator_id: Mapped[UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    enrolled_at: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    competitor: Mapped[CompetitorModel] = relationship(
        "CompetitorModel",
        back_populates="enrollments",
    )
    modality: Mapped[ModalityModel] = relationship(
        "ModalityModel",
        back_populates="enrollments",
    )
    evaluator: Mapped[UserModel] = relationship("UserModel", foreign_keys=[evaluator_id])

    __table_args__ = (
        Index(
            "ix_enrollments_competitor_modality",
            "competitor_id",
            "modality_id",
            unique=True,
        ),
        Index("ix_enrollments_evaluator_modality", "evaluator_id", "modality_id"),
    )


class EvaluatorModalityModel(Base):
    """Direct evaluator-modality assignment model."""

    __tablename__ = "evaluator_modalities"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    evaluator_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    modality_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("modalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    assigned_by: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    evaluator: Mapped[UserModel] = relationship(
        "UserModel",
        foreign_keys=[evaluator_id],
        backref="evaluator_modalities",
    )
    modality: Mapped[ModalityModel] = relationship(
        "ModalityModel",
        backref="evaluator_assignments",
    )

    __table_args__ = (
        Index(
            "ix_evaluator_modalities_evaluator_modality",
            "evaluator_id",
            "modality_id",
            unique=True,
        ),
    )


# Import UserModel for relationships
from src.infrastructure.database.models.user_model import UserModel  # noqa: E402
