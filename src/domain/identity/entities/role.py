"""Role entity."""

from datetime import datetime
from uuid import UUID

from src.domain.identity.entities.permission import Permission
from src.shared.constants.enums import UserRole
from src.shared.domain.entity import Entity


class Role(Entity[UUID]):
    """Role entity representing a set of permissions.

    Roles group permissions together for easier assignment to users.
    """

    def __init__(
        self,
        name: UserRole,
        description: str,
        permissions: list[Permission] | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._name = name
        self._description = description
        self._permissions: list[Permission] = permissions or []

    @property
    def name(self) -> UserRole:
        """Get role name."""
        return self._name

    @property
    def description(self) -> str:
        """Get role description."""
        return self._description

    @property
    def permissions(self) -> list[Permission]:
        """Get list of permissions for this role."""
        return self._permissions.copy()

    def has_permission(self, permission_code: str) -> bool:
        """Check if role has a specific permission.

        Args:
            permission_code: Permission code in format 'resource:action'.

        Returns:
            True if role has the permission.
        """
        return any(p.code == permission_code for p in self._permissions)

    def add_permission(self, permission: Permission) -> None:
        """Add a permission to this role.

        Args:
            permission: Permission to add.
        """
        if not self.has_permission(permission.code):
            self._permissions.append(permission)
            self._touch()

    def remove_permission(self, permission_code: str) -> bool:
        """Remove a permission from this role.

        Args:
            permission_code: Permission code to remove.

        Returns:
            True if permission was removed.
        """
        for i, p in enumerate(self._permissions):
            if p.code == permission_code:
                self._permissions.pop(i)
                self._touch()
                return True
        return False

    def __repr__(self) -> str:
        return f"Role(id={self._id}, name={self._name.value})"
