"""Unit of Work pattern implementation."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import async_session_factory


class AbstractUnitOfWork(ABC):
    """Abstract Unit of Work base class."""

    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy Unit of Work implementation.

    Manages database transactions and ensures consistency.
    """

    def __init__(self) -> None:
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        """Get the current session."""
        if self._session is None:
            raise RuntimeError("UnitOfWork not initialized. Use 'async with' context.")
        return self._session

    async def __aenter__(self) -> Self:
        """Enter the context and create a new session."""
        self._session = async_session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context, rollback if exception, close session."""
        if exc_type is not None:
            await self.rollback()
        await self._close()

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._session:
            await self._session.rollback()

    async def _close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None
