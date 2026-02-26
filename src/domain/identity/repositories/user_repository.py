"""User repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.identity.entities.user import User
from src.shared.constants.enums import UserRole
from src.shared.domain.repository import Repository


class UserRepository(Repository[User, UUID]):
    """Repository interface for User aggregate.

    Extends the base Repository with User-specific query methods.
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address.

        Args:
            email: User email address.

        Returns:
            User if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get users by role.

        Args:
            role: User role to filter by.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of users with the specified role.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get all users with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of users.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self) -> int:
        """Count total number of users.

        Returns:
            Total user count.
        """
        raise NotImplementedError

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email is already registered.

        Args:
            email: Email to check.

        Returns:
            True if email exists.
        """
        raise NotImplementedError
