"""Modality DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.application.modality.dtos.competence_dto import CompetenceDTO
from src.domain.modality.entities.modality import Modality


@dataclass(frozen=True)
class ModalityDTO:
    """Modality data transfer object."""

    id: UUID
    code: str
    name: str
    description: str
    is_active: bool
    min_training_hours: int | None
    competences: list[CompetenceDTO]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, modality: Modality) -> "ModalityDTO":
        """Create DTO from Modality entity."""
        return cls(
            id=modality.id,
            code=modality.code.value,
            name=modality.name,
            description=modality.description,
            is_active=modality.is_active,
            min_training_hours=modality.min_training_hours,
            competences=[CompetenceDTO.from_entity(c) for c in modality.competences],
            created_at=modality.created_at,
            updated_at=modality.updated_at,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "min_training_hours": self.min_training_hours,
            "competences": [c.to_dict() for c in self.competences],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class ModalityListDTO:
    """Modality list DTO with pagination."""

    modalities: list[ModalityDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more modalities."""
        return self.skip + len(self.modalities) < self.total


@dataclass(frozen=True)
class CreateModalityDTO:
    """DTO for creating a modality."""

    code: str
    name: str
    description: str
    min_training_hours: int | None = None


@dataclass(frozen=True)
class UpdateModalityDTO:
    """DTO for updating a modality."""

    code: str | None = None
    name: str | None = None
    description: str | None = None
    min_training_hours: int | None = None
    is_active: bool | None = None
