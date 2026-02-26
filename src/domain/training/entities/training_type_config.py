"""Training type configuration entity."""

from datetime import datetime
from uuid import UUID

from src.shared.domain.aggregate_root import AggregateRoot


class TrainingTypeConfig(AggregateRoot[UUID]):
    """Training type configuration entity.

    Allows administrators to configure which training types are available
    in the system (e.g., SENAI, FORA/External).
    """

    def __init__(
        self,
        code: str,
        name: str,
        description: str | None = None,
        is_active: bool = True,
        display_order: int = 0,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._code = code.lower().strip()
        self._name = name.strip()
        self._description = description.strip() if description else None
        self._is_active = is_active
        self._display_order = display_order

    @property
    def code(self) -> str:
        """Get training type code (unique identifier)."""
        return self._code

    @property
    def name(self) -> str:
        """Get training type display name."""
        return self._name

    @property
    def description(self) -> str | None:
        """Get training type description."""
        return self._description

    @property
    def is_active(self) -> bool:
        """Check if training type is active."""
        return self._is_active

    @property
    def display_order(self) -> int:
        """Get display order for UI."""
        return self._display_order

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        display_order: int | None = None,
    ) -> None:
        """Update training type details.

        Note: code cannot be changed after creation.
        """
        if name is not None:
            self._name = name.strip()
        if description is not None:
            self._description = description.strip() if description else None
        if display_order is not None:
            self._display_order = display_order
        self._touch()

    def activate(self) -> None:
        """Activate the training type."""
        self._is_active = True
        self._touch()

    def deactivate(self) -> None:
        """Deactivate the training type."""
        self._is_active = False
        self._touch()

    def __repr__(self) -> str:
        return f"TrainingTypeConfig(id={self._id}, code={self._code!r}, name={self._name!r})"
