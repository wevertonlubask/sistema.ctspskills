"""Grade DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.assessment.entities.grade import Grade
from src.domain.assessment.entities.grade_audit_log import GradeAuditLog


@dataclass
class RegisterGradeDTO:
    """DTO for registering a grade."""

    exam_id: UUID
    competitor_id: UUID
    competence_id: UUID
    score: float
    notes: str | None = None


@dataclass
class UpdateGradeDTO:
    """DTO for updating a grade."""

    score: float | None = None
    notes: str | None = None


@dataclass
class GradeDTO:
    """DTO for grade data."""

    id: UUID
    exam_id: UUID
    competitor_id: UUID
    competence_id: UUID
    score: float
    notes: str | None
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: Grade) -> "GradeDTO":
        """Create DTO from entity."""
        return cls(
            id=entity.id,
            exam_id=entity.exam_id,
            competitor_id=entity.competitor_id,
            competence_id=entity.competence_id,
            score=entity.score.value,
            notes=entity.notes,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass
class GradeListDTO:
    """DTO for paginated list of grades."""

    grades: list[GradeDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more results."""
        return self.skip + len(self.grades) < self.total


@dataclass
class GradeAuditDTO:
    """DTO for grade audit log data."""

    id: UUID
    grade_id: UUID
    action: str
    old_score: float | None
    new_score: float | None
    old_notes: str | None
    new_notes: str | None
    changed_by: UUID
    ip_address: str | None
    user_agent: str | None
    changed_at: datetime

    @classmethod
    def from_entity(cls, entity: GradeAuditLog) -> "GradeAuditDTO":
        """Create DTO from entity."""
        return cls(
            id=entity.id,
            grade_id=entity.grade_id,
            action=entity.action,
            old_score=entity.old_score,
            new_score=entity.new_score,
            old_notes=entity.old_notes,
            new_notes=entity.new_notes,
            changed_by=entity.changed_by,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,
            changed_at=entity.changed_at,
        )


@dataclass
class GradeHistoryDTO:
    """DTO for grade history."""

    grade: GradeDTO
    history: list[GradeAuditDTO]
