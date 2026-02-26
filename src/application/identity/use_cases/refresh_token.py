"""Refresh token use case."""

from src.application.identity.dtos.auth_dto import RefreshTokenDTO
from src.application.identity.dtos.token_dto import TokenPairDTO
from src.domain.identity.entities.refresh_token import RefreshToken
from src.domain.identity.repositories.refresh_token_repository import RefreshTokenRepository
from src.domain.identity.repositories.user_repository import UserRepository
from src.infrastructure.security.jwt_handler import JWTHandler
from src.shared.exceptions import AuthenticationException, ErrorCode


class RefreshTokenUseCase:
    """Use case for refreshing access tokens."""

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_handler: JWTHandler,
    ) -> None:
        self._user_repository = user_repository
        self._refresh_token_repository = refresh_token_repository
        self._jwt_handler = jwt_handler

    async def execute(
        self,
        dto: RefreshTokenDTO,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPairDTO:
        """Refresh access token using refresh token.

        Args:
            dto: Refresh token data.
            user_agent: Client user agent.
            ip_address: Client IP address.

        Returns:
            New token pair.

        Raises:
            AuthenticationException: If refresh token is invalid or revoked.
        """
        # Verify refresh token format
        self._jwt_handler.verify_refresh_token(dto.refresh_token)

        # Get stored refresh token
        stored_token = await self._refresh_token_repository.get_by_token(dto.refresh_token)

        if not stored_token:
            raise AuthenticationException(
                message="Refresh token not found",
                code=ErrorCode.TOKEN_INVALID,
            )

        if not stored_token.is_valid:
            raise AuthenticationException(
                message="Refresh token is revoked or expired",
                code=ErrorCode.TOKEN_REVOKED,
            )

        # Get user
        user = await self._user_repository.get_by_id(stored_token.user_id)

        if not user:
            raise AuthenticationException(
                message="User not found",
                code=ErrorCode.TOKEN_INVALID,
            )

        # Check if user is still active
        user.ensure_active()

        # Revoke old refresh token
        stored_token.revoke()
        await self._refresh_token_repository.update(stored_token)

        # Create new tokens
        access_token, access_expires = self._jwt_handler.create_access_token(
            user_id=user.id,
            role=user.role.value,
        )

        new_refresh_token_str, refresh_expires = self._jwt_handler.create_refresh_token(
            user_id=user.id,
        )

        # Store new refresh token
        new_refresh_token = RefreshToken(
            user_id=user.id,
            token=new_refresh_token_str,
            expires_at=refresh_expires,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self._refresh_token_repository.add(new_refresh_token)

        return TokenPairDTO(
            access_token=access_token,
            refresh_token=new_refresh_token_str,
            expires_at=access_expires,
        )
