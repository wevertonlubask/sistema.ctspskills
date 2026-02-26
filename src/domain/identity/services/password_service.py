"""Password domain service interface."""

from abc import ABC, abstractmethod


class PasswordService(ABC):
    """Abstract password service for hashing and verification.

    This is a domain service interface. The implementation
    resides in the infrastructure layer.
    """

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password.

        Args:
            plain_password: The plain text password to hash.

        Returns:
            The hashed password.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hash.

        Args:
            plain_password: The plain text password to verify.
            hashed_password: The hashed password to compare against.

        Returns:
            True if password matches, False otherwise.
        """
        raise NotImplementedError
