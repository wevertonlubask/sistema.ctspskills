"""Resource repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.extras.entities.resource import Resource
from src.shared.constants.enums import ResourceType


class ResourceRepository(ABC):
    """Abstract repository for resources."""

    @abstractmethod
    async def save(self, resource: Resource) -> Resource:
        """Save a resource."""
        ...

    @abstractmethod
    async def get_by_id(self, resource_id: UUID) -> Resource | None:
        """Get resource by ID."""
        ...

    @abstractmethod
    async def get_by_modality(
        self,
        modality_id: UUID,
        resource_type: ResourceType | None = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Resource]:
        """Get resources for a modality."""
        ...

    @abstractmethod
    async def get_public(
        self,
        resource_type: ResourceType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Resource]:
        """Get public resources."""
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        modality_id: UUID | None = None,
        resource_type: ResourceType | None = None,
        tags: list[str] | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Resource]:
        """Search resources."""
        ...

    @abstractmethod
    async def get_by_tags(
        self,
        tags: list[str],
        modality_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Resource]:
        """Get resources by tags."""
        ...

    @abstractmethod
    async def update(self, resource: Resource) -> Resource:
        """Update a resource."""
        ...

    @abstractmethod
    async def delete(self, resource_id: UUID) -> bool:
        """Delete a resource."""
        ...

    @abstractmethod
    async def increment_view_count(self, resource_id: UUID) -> bool:
        """Increment view count."""
        ...

    @abstractmethod
    async def increment_download_count(self, resource_id: UUID) -> bool:
        """Increment download count."""
        ...

    @abstractmethod
    async def get_popular(
        self,
        modality_id: UUID | None = None,
        limit: int = 10,
    ) -> list[Resource]:
        """Get popular resources by view/download count."""
        ...
