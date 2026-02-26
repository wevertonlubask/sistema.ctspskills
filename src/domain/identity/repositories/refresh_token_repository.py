"""Refresh token repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.identity.entities.refresh_token import RefreshToken
from src.shared.domain.repository import Repository


class RefreshTokenRepository(Repository[RefreshToken, UUID]):
    """Repository interface for RefreshToken entity."""

    @abstractmethod
    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Get refresh token by token string.

        Args:
            token: The token string.

        Returns:
            RefreshToken if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[RefreshToken]:
        """Get all refresh tokens for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of refresh tokens.
        """
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user.

        Args:
            user_id: User identifier.

        Returns:
            Number of tokens revoked.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_expired(self) -> int:
        """Delete all expired tokens.

        Returns:
            Number of tokens deleted.
        """
        raise NotImplementedError
