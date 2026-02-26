"""Training type config DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.training.entities.training_type_config import TrainingTypeConfig


@dataclass(frozen=True)
class TrainingTypeConfigDTO:
    """DTO for TrainingTypeConfig entity."""

    id: UUID
    code: str
    name: str
    description: str | None
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: TrainingTypeConfig) -> "TrainingTypeConfigDTO":
        """Create DTO from entity."""
        return cls(
            id=entity.id,
            code=entity.code,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            display_order=entity.display_order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass(frozen=True)
class TrainingTypeConfigListDTO:
    """DTO for paginated list of training types."""

    items: list[TrainingTypeConfigDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more items."""
        return self.skip + len(self.items) < self.total
