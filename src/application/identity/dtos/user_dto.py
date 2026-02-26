"""User DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.identity.entities.user import User
from src.shared.constants.enums import UserRole, UserStatus


@dataclass(frozen=True)
class UserDTO:
    """User data transfer object."""

    id: UUID
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None
    must_change_password: bool = False

    @classmethod
    def from_entity(cls, user: User) -> "UserDTO":
        """Create DTO from User entity.

        Args:
            user: User entity.

        Returns:
            UserDTO instance.
        """
        return cls(
            id=user.id,
            email=user.email.value,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            must_change_password=user.must_change_password,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "must_change_password": self.must_change_password,
        }


@dataclass(frozen=True)
class UserListDTO:
    """User list data transfer object with pagination info."""

    users: list[UserDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more users to fetch."""
        return self.skip + len(self.users) < self.total
