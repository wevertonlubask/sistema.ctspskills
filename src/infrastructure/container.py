"""Dependency Injection Container."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity.repositories.refresh_token_repository import RefreshTokenRepository
from src.domain.identity.repositories.user_repository import UserRepository
from src.domain.identity.services.password_service import PasswordService
from src.infrastructure.database.repositories.refresh_token_repository_impl import (
    SQLAlchemyRefreshTokenRepository,
)
from src.infrastructure.database.repositories.user_repository_impl import (
    SQLAlchemyUserRepository,
)
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import BcryptPasswordHasher

T = TypeVar("T")


class Singleton(Generic[T]):
    """Simple singleton container."""

    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory
        self._instance: T | None = None

    def get(self) -> T:
        """Get or create the singleton instance."""
        if self._instance is None:
            self._instance = self._factory()
        return self._instance

    def reset(self) -> None:
        """Reset the singleton instance."""
        self._instance = None


@dataclass
class Container:
    """Dependency injection container.

    This container manages the creation and lifecycle of dependencies.
    It provides both singleton and per-request scoped dependencies.
    """

    # Singletons (application-scoped)
    _password_service: Singleton[PasswordService] = None  # type: ignore
    _jwt_handler: Singleton[JWTHandler] = None  # type: ignore

    def __post_init__(self) -> None:
        """Initialize singleton factories."""
        self._password_service = Singleton(lambda: BcryptPasswordHasher())
        self._jwt_handler = Singleton(lambda: JWTHandler())

    @property
    def password_service(self) -> PasswordService:
        """Get password service singleton."""
        return self._password_service.get()

    @property
    def jwt_handler(self) -> JWTHandler:
        """Get JWT handler singleton."""
        return self._jwt_handler.get()

    def user_repository(self, session: AsyncSession) -> UserRepository:
        """Create a user repository for the given session.

        Args:
            session: Database session.

        Returns:
            UserRepository instance.
        """
        return SQLAlchemyUserRepository(session)

    def refresh_token_repository(self, session: AsyncSession) -> RefreshTokenRepository:
        """Create a refresh token repository for the given session.

        Args:
            session: Database session.

        Returns:
            RefreshTokenRepository instance.
        """
        return SQLAlchemyRefreshTokenRepository(session)


# Global container instance
container = Container()


def get_container() -> Container:
    """Get the global container instance."""
    return container
