"""Authentication DTOs."""

from dataclasses import dataclass

from src.shared.constants.enums import UserRole


@dataclass(frozen=True)
class RegisterUserDTO:
    """Data for registering a new user."""

    email: str
    password: str
    full_name: str
    role: UserRole = UserRole.COMPETITOR
    must_change_password: bool = False


@dataclass(frozen=True)
class LoginDTO:
    """Data for user login."""

    email: str
    password: str


@dataclass(frozen=True)
class RefreshTokenDTO:
    """Data for refreshing tokens."""

    refresh_token: str


@dataclass(frozen=True)
class LogoutDTO:
    """Data for user logout."""

    refresh_token: str


@dataclass(frozen=True)
class ChangePasswordDTO:
    """Data for changing user password."""

    current_password: str
    new_password: str
