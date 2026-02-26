"""Base Repository interface."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from src.shared.domain.entity import Entity

EntityType = TypeVar("EntityType", bound=Entity)
IdType = TypeVar("IdType", bound=UUID | int | str)


class Repository(ABC, Generic[EntityType, IdType]):
    """Base repository interface for data persistence.

    Repositories provide a collection-like interface for accessing
    domain entities. They encapsulate the logic required to access
    data sources.
    """

    @abstractmethod
    async def get_by_id(self, id: IdType) -> EntityType | None:
        """Get entity by ID.

        Args:
            id: Entity identifier.

        Returns:
            Entity if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def add(self, entity: EntityType) -> EntityType:
        """Add a new entity.

        Args:
            entity: Entity to add.

        Returns:
            Added entity with any generated values.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: EntityType) -> EntityType:
        """Update an existing entity.

        Args:
            entity: Entity to update.

        Returns:
            Updated entity.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: IdType) -> bool:
        """Delete an entity by ID.

        Args:
            id: Entity identifier.

        Returns:
            True if entity was deleted, False if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def exists(self, id: IdType) -> bool:
        """Check if entity exists.

        Args:
            id: Entity identifier.

        Returns:
            True if entity exists, False otherwise.
        """
        raise NotImplementedError
