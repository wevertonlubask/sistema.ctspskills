"""Database dependencies."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import get_async_session
from src.infrastructure.database.unit_of_work import UnitOfWork


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        AsyncSession: Database session.
    """
    async for session in get_async_session():
        yield session


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Get Unit of Work dependency.

    Yields:
        UnitOfWork: Unit of work instance.
    """
    async with UnitOfWork() as uow:
        yield uow
