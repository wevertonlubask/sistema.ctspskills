"""JWT token handling."""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from jose import JWTError, jwt

from src.config.settings import get_settings
from src.shared.constants.enums import TokenType
from src.shared.exceptions import AuthenticationException, ErrorCode
from src.shared.utils.date_utils import utc_now

settings = get_settings()


class JWTHandler:
    """Handler for JWT token operations."""

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_token_expire_minutes: int | None = None,
        refresh_token_expire_days: int | None = None,
    ) -> None:
        self._secret_key = secret_key or settings.jwt_secret_key
        self._algorithm = algorithm or settings.jwt_algorithm
        self._access_token_expire_minutes = (
            access_token_expire_minutes or settings.access_token_expire_minutes
        )
        self._refresh_token_expire_days = (
            refresh_token_expire_days or settings.refresh_token_expire_days
        )

    def create_access_token(
        self,
        user_id: UUID,
        role: str,
        additional_claims: dict[str, Any] | None = None,
    ) -> tuple[str, datetime]:
        """Create an access token.

        Args:
            user_id: User identifier.
            role: User role.
            additional_claims: Additional claims to include in token.

        Returns:
            Tuple of (token string, expiration datetime).
        """
        expires_at = utc_now() + timedelta(minutes=self._access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": TokenType.ACCESS.value,
            "exp": expires_at,
            "iat": utc_now(),
            "jti": str(uuid4()),
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token, expires_at

    def create_refresh_token(
        self,
        user_id: UUID,
    ) -> tuple[str, datetime]:
        """Create a refresh token.

        Args:
            user_id: User identifier.

        Returns:
            Tuple of (token string, expiration datetime).
        """
        expires_at = utc_now() + timedelta(days=self._refresh_token_expire_days)
        payload = {
            "sub": str(user_id),
            "type": TokenType.REFRESH.value,
            "exp": expires_at,
            "iat": utc_now(),
            "jti": str(uuid4()),
        }

        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token, expires_at

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT token.

        Args:
            token: The JWT token string.

        Returns:
            Token payload.

        Raises:
            AuthenticationException: If token is invalid or expired.
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            return payload
        except JWTError as e:
            if "expired" in str(e).lower():
                raise AuthenticationException(
                    message="Token has expired",
                    code=ErrorCode.TOKEN_EXPIRED,
                ) from e
            raise AuthenticationException(
                message="Invalid token",
                code=ErrorCode.TOKEN_INVALID,
            ) from e

    def verify_access_token(self, token: str) -> dict[str, Any]:
        """Verify an access token.

        Args:
            token: The access token string.

        Returns:
            Token payload.

        Raises:
            AuthenticationException: If token is invalid or not an access token.
        """
        payload = self.decode_token(token)

        if payload.get("type") != TokenType.ACCESS.value:
            raise AuthenticationException(
                message="Invalid token type",
                code=ErrorCode.TOKEN_INVALID,
            )

        return payload

    def verify_refresh_token(self, token: str) -> dict[str, Any]:
        """Verify a refresh token.

        Args:
            token: The refresh token string.

        Returns:
            Token payload.

        Raises:
            AuthenticationException: If token is invalid or not a refresh token.
        """
        payload = self.decode_token(token)

        if payload.get("type") != TokenType.REFRESH.value:
            raise AuthenticationException(
                message="Invalid token type",
                code=ErrorCode.TOKEN_INVALID,
            )

        return payload

    def get_user_id_from_token(self, token: str) -> UUID:
        """Extract user ID from token.

        Args:
            token: The JWT token string.

        Returns:
            User UUID.

        Raises:
            AuthenticationException: If token is invalid.
        """
        payload = self.decode_token(token)
        user_id_str = payload.get("sub")

        if not user_id_str:
            raise AuthenticationException(
                message="Invalid token payload",
                code=ErrorCode.TOKEN_INVALID,
            )

        try:
            return UUID(user_id_str)
        except ValueError as e:
            raise AuthenticationException(
                message="Invalid user ID in token",
                code=ErrorCode.TOKEN_INVALID,
            ) from e
