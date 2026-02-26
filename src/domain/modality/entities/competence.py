"""Competence entity."""

from datetime import datetime
from uuid import UUID

from src.shared.domain.entity import Entity


class Competence(Entity[UUID]):
    """Competence entity representing a skill that can be evaluated.

    Competences are specific skills within a modality that competitors
    are evaluated on during training and competitions.
    """

    def __init__(
        self,
        name: str,
        description: str,
        modality_id: UUID,
        weight: float = 1.0,
        max_score: float = 100.0,
        is_active: bool = True,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._name = name.strip()
        self._description = description.strip()
        self._modality_id = modality_id
        self._weight = weight
        self._max_score = max_score
        self._is_active = is_active

    @property
    def name(self) -> str:
        """Get competence name."""
        return self._name

    @property
    def description(self) -> str:
        """Get competence description."""
        return self._description

    @property
    def modality_id(self) -> UUID:
        """Get modality ID this competence belongs to."""
        return self._modality_id

    @property
    def weight(self) -> float:
        """Get competence weight for scoring."""
        return self._weight

    @property
    def max_score(self) -> float:
        """Get maximum score for this competence."""
        return self._max_score

    @property
    def is_active(self) -> bool:
        """Check if competence is active."""
        return self._is_active

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        weight: float | None = None,
        max_score: float | None = None,
    ) -> None:
        """Update competence details."""
        if name is not None:
            self._name = name.strip()
        if description is not None:
            self._description = description.strip()
        if weight is not None:
            self._weight = weight
        if max_score is not None:
            self._max_score = max_score
        self._touch()

    def activate(self) -> None:
        """Activate the competence."""
        self._is_active = True
        self._touch()

    def deactivate(self) -> None:
        """Deactivate the competence."""
        self._is_active = False
        self._touch()

    def __repr__(self) -> str:
        return f"Competence(id={self._id}, name={self._name!r})"
