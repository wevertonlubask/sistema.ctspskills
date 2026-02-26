"""Login user use case."""


from src.application.identity.dtos.auth_dto import LoginDTO
from src.application.identity.dtos.token_dto import TokenPairDTO, TokenResponseDTO
from src.application.identity.dtos.user_dto import UserDTO
from src.domain.identity.entities.refresh_token import RefreshToken
from src.domain.identity.repositories.refresh_token_repository import RefreshTokenRepository
from src.domain.identity.repositories.user_repository import UserRepository
from src.domain.identity.services.password_service import PasswordService
from src.infrastructure.security.jwt_handler import JWTHandler
from src.shared.exceptions import AuthenticationException, ErrorCode
from src.shared.utils.date_utils import utc_now


class LoginUserUseCase:
    """Use case for user login."""

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        password_service: PasswordService,
        jwt_handler: JWTHandler,
    ) -> None:
        self._user_repository = user_repository
        self._refresh_token_repository = refresh_token_repository
        self._password_service = password_service
        self._jwt_handler = jwt_handler

    async def execute(
        self,
        dto: LoginDTO,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponseDTO:
        """Authenticate user and return tokens.

        Args:
            dto: Login credentials.
            user_agent: Client user agent.
            ip_address: Client IP address.

        Returns:
            Token response with user info.

        Raises:
            AuthenticationException: If credentials are invalid.
            UserInactiveException: If user account is not active.
        """
        # Find user by email
        user = await self._user_repository.get_by_email(dto.email)

        if not user:
            raise AuthenticationException(
                message="Invalid email or password",
                code=ErrorCode.INVALID_CREDENTIALS,
            )

        # Verify password
        if not self._password_service.verify_password(
            dto.password,
            user.password.hashed_value,
        ):
            raise AuthenticationException(
                message="Invalid email or password",
                code=ErrorCode.INVALID_CREDENTIALS,
            )

        # Check if user is active
        user.ensure_active()

        # Record login
        user.record_login(utc_now())
        await self._user_repository.update(user)

        # Create tokens
        access_token, access_expires = self._jwt_handler.create_access_token(
            user_id=user.id,
            role=user.role.value,
        )

        refresh_token_str, refresh_expires = self._jwt_handler.create_refresh_token(
            user_id=user.id,
        )

        # Store refresh token
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=refresh_expires,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self._refresh_token_repository.add(refresh_token)

        return TokenResponseDTO(
            tokens=TokenPairDTO(
                access_token=access_token,
                refresh_token=refresh_token_str,
                expires_at=access_expires,
            ),
            user=UserDTO.from_entity(user),
        )
