"""Exam DTOs."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.domain.assessment.entities.exam import Exam
from src.shared.constants.enums import AssessmentType


@dataclass
class CreateExamDTO:
    """DTO for creating an exam."""

    name: str
    modality_id: UUID
    assessment_type: AssessmentType
    exam_date: date
    description: str | None = None
    competence_ids: list[UUID] | None = None


@dataclass
class UpdateExamDTO:
    """DTO for updating an exam."""

    name: str | None = None
    description: str | None = None
    exam_date: date | None = None
    assessment_type: AssessmentType | None = None
    competence_ids: list[UUID] | None = None
    is_active: bool | None = None


@dataclass
class ExamDTO:
    """DTO for exam data."""

    id: UUID
    name: str
    description: str | None
    modality_id: UUID
    assessment_type: AssessmentType
    exam_date: date
    is_active: bool
    competence_ids: list[UUID]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: Exam) -> "ExamDTO":
        """Create DTO from entity."""
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            modality_id=entity.modality_id,
            assessment_type=entity.assessment_type,
            exam_date=entity.exam_date,
            is_active=entity.is_active,
            competence_ids=entity.competence_ids,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass
class ExamListDTO:
    """DTO for paginated list of exams."""

    exams: list[ExamDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more results."""
        return self.skip + len(self.exams) < self.total
