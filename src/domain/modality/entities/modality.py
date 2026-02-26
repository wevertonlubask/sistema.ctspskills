"""Modality entity - Aggregate Root."""

from datetime import datetime
from uuid import UUID

from src.domain.modality.entities.competence import Competence
from src.domain.modality.value_objects.modality_code import ModalityCode
from src.shared.domain.aggregate_root import AggregateRoot


class Modality(AggregateRoot[UUID]):
    """Modality aggregate root.

    Represents a competition modality/occupation (e.g., Web Development,
    Industrial Mechanics) with its competences.
    """

    def __init__(
        self,
        code: ModalityCode,
        name: str,
        description: str,
        is_active: bool = True,
        min_training_hours: int | None = None,
        competences: list[Competence] | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._code = code
        self._name = name.strip()
        self._description = description.strip()
        self._is_active = is_active
        self._min_training_hours = min_training_hours
        self._competences: list[Competence] = competences or []

    @property
    def code(self) -> ModalityCode:
        """Get modality code."""
        return self._code

    @property
    def name(self) -> str:
        """Get modality name."""
        return self._name

    @property
    def description(self) -> str:
        """Get modality description."""
        return self._description

    @property
    def is_active(self) -> bool:
        """Check if modality is active."""
        return self._is_active

    @property
    def min_training_hours(self) -> int | None:
        """Get minimum training hours required."""
        return self._min_training_hours

    @property
    def competences(self) -> list[Competence]:
        """Get list of competences."""
        return self._competences.copy()

    @property
    def active_competences(self) -> list[Competence]:
        """Get list of active competences."""
        return [c for c in self._competences if c.is_active]

    def update(
        self,
        code: ModalityCode | None = None,
        name: str | None = None,
        description: str | None = None,
        min_training_hours: int | None = None,
    ) -> None:
        """Update modality details."""
        if code is not None:
            self._code = code
        if name is not None:
            self._name = name.strip()
        if description is not None:
            self._description = description.strip()
        if min_training_hours is not None:
            self._min_training_hours = min_training_hours
        self._touch()

    def activate(self) -> None:
        """Activate the modality."""
        self._is_active = True
        self._touch()

    def deactivate(self) -> None:
        """Deactivate the modality."""
        self._is_active = False
        self._touch()

    def add_competence(self, competence: Competence) -> None:
        """Add a competence to this modality.

        Args:
            competence: Competence to add.
        """
        if not any(c.id == competence.id for c in self._competences):
            self._competences.append(competence)
            self._touch()

    def remove_competence(self, competence_id: UUID) -> bool:
        """Remove a competence from this modality.

        Args:
            competence_id: ID of competence to remove.

        Returns:
            True if competence was removed.
        """
        for i, c in enumerate(self._competences):
            if c.id == competence_id:
                self._competences.pop(i)
                self._touch()
                return True
        return False

    def get_competence(self, competence_id: UUID) -> Competence | None:
        """Get a competence by ID.

        Args:
            competence_id: Competence ID.

        Returns:
            Competence if found.
        """
        for c in self._competences:
            if c.id == competence_id:
                return c
        return None

    def has_competence(self, competence_id: UUID) -> bool:
        """Check if modality has a specific competence.

        Args:
            competence_id: Competence ID to check.

        Returns:
            True if modality has the competence.
        """
        return any(c.id == competence_id for c in self._competences)

    def __repr__(self) -> str:
        return f"Modality(id={self._id}, code={self._code}, name={self._name!r})"
