"""Permission entity."""

from datetime import datetime
from uuid import UUID

from src.shared.domain.entity import Entity


class Permission(Entity[UUID]):
    """Permission entity representing a specific action a user can perform.

    Permissions are granular access rights that can be assigned to roles.
    """

    def __init__(
        self,
        name: str,
        description: str,
        resource: str,
        action: str,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._name = name
        self._description = description
        self._resource = resource
        self._action = action

    @property
    def name(self) -> str:
        """Get permission name."""
        return self._name

    @property
    def description(self) -> str:
        """Get permission description."""
        return self._description

    @property
    def resource(self) -> str:
        """Get resource this permission applies to."""
        return self._resource

    @property
    def action(self) -> str:
        """Get action this permission allows."""
        return self._action

    @property
    def code(self) -> str:
        """Get permission code (resource:action format)."""
        return f"{self._resource}:{self._action}"

    def __repr__(self) -> str:
        return f"Permission(id={self._id}, code={self.code})"
