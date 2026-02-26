"""Logout user use case."""

from uuid import UUID

from src.application.identity.dtos.auth_dto import LogoutDTO
from src.domain.identity.repositories.refresh_token_repository import RefreshTokenRepository


class LogoutUserUseCase:
    """Use case for user logout."""

    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self._refresh_token_repository = refresh_token_repository

    async def execute(self, dto: LogoutDTO) -> bool:
        """Logout user by revoking refresh token.

        Args:
            dto: Logout data with refresh token.

        Returns:
            True if logout was successful.

        Raises:
            AuthenticationException: If refresh token is not found.
        """
        # Find refresh token
        token = await self._refresh_token_repository.get_by_token(dto.refresh_token)

        if not token:
            # Token not found, consider it already logged out
            return True

        if token.is_revoked:
            # Already revoked
            return True

        # Revoke the token
        token.revoke()
        await self._refresh_token_repository.update(token)

        return True

    async def logout_all_sessions(self, user_id: UUID) -> int:
        """Logout user from all sessions.

        Args:
            user_id: User identifier.

        Returns:
            Number of sessions logged out.
        """
        return await self._refresh_token_repository.revoke_all_for_user(user_id)
