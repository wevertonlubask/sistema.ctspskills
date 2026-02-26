"""Competence DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.modality.entities.competence import Competence


@dataclass(frozen=True)
class CompetenceDTO:
    """Competence data transfer object."""

    id: UUID
    modality_id: UUID
    name: str
    description: str
    weight: float
    max_score: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, competence: Competence) -> "CompetenceDTO":
        """Create DTO from Competence entity."""
        return cls(
            id=competence.id,
            modality_id=competence.modality_id,
            name=competence.name,
            description=competence.description,
            weight=competence.weight,
            max_score=competence.max_score,
            is_active=competence.is_active,
            created_at=competence.created_at,
            updated_at=competence.updated_at,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "modality_id": str(self.modality_id),
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "max_score": self.max_score,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class CreateCompetenceDTO:
    """DTO for creating a competence."""

    name: str
    description: str
    weight: float = 1.0
    max_score: float = 100.0


@dataclass(frozen=True)
class UpdateCompetenceDTO:
    """DTO for updating a competence."""

    name: str | None = None
    description: str | None = None
    weight: float | None = None
    max_score: float | None = None
    is_active: bool | None = None
