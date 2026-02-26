"""Assessment-related SQLAlchemy models."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import GUID, Base
from src.shared.utils.date_utils import utc_now

# Association table for Exam-Competence many-to-many relationship
exam_competences = Table(
    "exam_competences",
    Base.metadata,
    Column(
        "exam_id",
        GUID,
        ForeignKey("exams.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "competence_id",
        GUID,
        ForeignKey("competences.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ExamModel(Base):
    """Exam database model."""

    __tablename__ = "exams"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    modality_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("modalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessment_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    exam_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
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
    modality: Mapped["ModalityModel"] = relationship(
        "ModalityModel",
        back_populates="exams",
    )
    creator: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[created_by],
    )
    competences: Mapped[list["CompetenceModel"]] = relationship(
        "CompetenceModel",
        secondary=exam_competences,
        backref="exams",
    )
    grades: Mapped[list["GradeModel"]] = relationship(
        "GradeModel",
        back_populates="exam",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_exams_modality_date", "modality_id", "exam_date"),
        Index("ix_exams_active", "is_active"),
        Index("ix_exams_type_date", "assessment_type", "exam_date"),
    )


class GradeModel(Base):
    """Grade database model."""

    __tablename__ = "grades"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    exam_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    competitor_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    competence_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("competences.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    updated_by: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
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
    exam: Mapped[ExamModel] = relationship(
        "ExamModel",
        back_populates="grades",
    )
    competitor: Mapped["CompetitorModel"] = relationship(
        "CompetitorModel",
        backref="grades",
    )
    competence: Mapped["CompetenceModel"] = relationship(
        "CompetenceModel",
        backref="grades",
    )
    creator: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[created_by],
    )
    updater: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[updated_by],
    )
    audit_logs: Mapped[list["GradeAuditLogModel"]] = relationship(
        "GradeAuditLogModel",
        back_populates="grade",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "exam_id",
            "competitor_id",
            "competence_id",
            name="uq_grades_exam_competitor_competence",
        ),
        Index("ix_grades_exam_competitor", "exam_id", "competitor_id"),
        Index("ix_grades_exam_competence", "exam_id", "competence_id"),
        Index("ix_grades_competitor_competence", "competitor_id", "competence_id"),
    )


class GradeAuditLogModel(Base):
    """Grade audit log database model."""

    __tablename__ = "grade_audit_logs"

    id: Mapped[UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid4,
    )
    grade_id: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("grades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    old_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    old_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    # Relationships
    grade: Mapped[GradeModel] = relationship(
        "GradeModel",
        back_populates="audit_logs",
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[changed_by],
    )

    __table_args__ = (
        Index("ix_audit_grade_time", "grade_id", "changed_at"),
        Index("ix_audit_user_time", "changed_by", "changed_at"),
    )


# Import related models for relationships
from src.infrastructure.database.models.modality_model import (  # noqa: E402
    CompetenceModel,
    CompetitorModel,
    ModalityModel,
)
from src.infrastructure.database.models.user_model import UserModel  # noqa: E402
