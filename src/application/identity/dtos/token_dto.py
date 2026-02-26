"""Token DTOs."""

from dataclasses import dataclass
from datetime import datetime

from src.application.identity.dtos.user_dto import UserDTO


@dataclass(frozen=True)
class TokenPairDTO:
    """Token pair data transfer object."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


@dataclass(frozen=True)
class TokenResponseDTO:
    """Token response with user info."""

    tokens: TokenPairDTO
    user: UserDTO

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            **self.tokens.to_dict(),
            "user": self.user.to_dict(),
        }
