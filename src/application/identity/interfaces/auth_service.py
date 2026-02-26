"""Authentication service interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.application.identity.dtos.token_dto import TokenPairDTO


class AuthService(ABC):
    """Abstract authentication service."""

    @abstractmethod
    def create_tokens(self, user_id: UUID, role: str) -> TokenPairDTO:
        """Create access and refresh tokens.

        Args:
            user_id: User identifier.
            role: User role.

        Returns:
            TokenPairDTO with access and refresh tokens.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_access_token(self, token: str) -> dict:
        """Verify access token.

        Args:
            token: Access token string.

        Returns:
            Token payload.

        Raises:
            AuthenticationException: If token is invalid.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_refresh_token(self, token: str) -> dict:
        """Verify refresh token.

        Args:
            token: Refresh token string.

        Returns:
            Token payload.

        Raises:
            AuthenticationException: If token is invalid.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> UUID:
        """Extract user ID from token.

        Args:
            token: Token string.

        Returns:
            User UUID.

        Raises:
            AuthenticationException: If token is invalid.
        """
        raise NotImplementedError
