"""Refresh Token entity."""

from datetime import datetime
from uuid import UUID

from src.shared.domain.entity import Entity
from src.shared.utils.date_utils import to_utc, utc_now


class RefreshToken(Entity[UUID]):
    """Refresh token entity for JWT authentication.

    Stores refresh tokens in database to allow revocation and tracking.
    """

    def __init__(
        self,
        user_id: UUID,
        token: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
        is_revoked: bool = False,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._user_id = user_id
        self._token = token
        self._expires_at = expires_at
        self._user_agent = user_agent
        self._ip_address = ip_address
        self._is_revoked = is_revoked

    @property
    def user_id(self) -> UUID:
        """Get user ID this token belongs to."""
        return self._user_id

    @property
    def token(self) -> str:
        """Get the token string."""
        return self._token

    @property
    def expires_at(self) -> datetime:
        """Get token expiration datetime."""
        return self._expires_at

    @property
    def user_agent(self) -> str | None:
        """Get user agent that created this token."""
        return self._user_agent

    @property
    def ip_address(self) -> str | None:
        """Get IP address that created this token."""
        return self._ip_address

    @property
    def is_revoked(self) -> bool:
        """Check if token is revoked."""
        return self._is_revoked

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return utc_now() > to_utc(self._expires_at)

    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not revoked and not expired)."""
        return not self._is_revoked and not self.is_expired

    def revoke(self) -> None:
        """Revoke this token."""
        self._is_revoked = True
        self._touch()

    def __repr__(self) -> str:
        return f"RefreshToken(id={self._id}, user_id={self._user_id}, valid={self.is_valid})"
