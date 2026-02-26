"""Resource use cases."""

from uuid import UUID

from src.application.extras.dtos.resource_dto import (
    CreateResourceDTO,
    ResourceDTO,
    ResourceListDTO,
)
from src.domain.extras.entities.resource import Resource
from src.domain.extras.exceptions import ResourceAccessDeniedException, ResourceNotFoundException
from src.domain.extras.repositories.resource_repository import ResourceRepository
from src.shared.constants.enums import ResourceType


class CreateResourceUseCase:
    """Use case for creating resources."""

    def __init__(self, resource_repository: ResourceRepository) -> None:
        self._resource_repository = resource_repository

    async def execute(
        self,
        creator_id: UUID,
        dto: CreateResourceDTO,
    ) -> ResourceDTO:
        """Create a resource.

        Args:
            creator_id: Creator user UUID.
            dto: Resource data.

        Returns:
            Created resource DTO.
        """
        resource = Resource(
            title=dto.title,
            resource_type=dto.resource_type,
            description=dto.description,
            url=dto.url,
            file_path=dto.file_path,
            file_size=dto.file_size,
            mime_type=dto.mime_type,
            modality_id=dto.modality_id,
            access_level=dto.access_level,
            tags=dto.tags,
            created_by=creator_id,
        )

        saved = await self._resource_repository.save(resource)
        return ResourceDTO.from_entity(saved)


class ListResourcesUseCase:
    """Use case for listing resources."""

    def __init__(self, resource_repository: ResourceRepository) -> None:
        self._resource_repository = resource_repository

    async def execute(
        self,
        modality_id: UUID | None = None,
        resource_type: ResourceType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ResourceListDTO:
        """List resources.

        Args:
            modality_id: Optional modality filter.
            resource_type: Optional resource type filter.
            skip: Number of items to skip.
            limit: Maximum items to return.

        Returns:
            Resource list DTO.
        """
        if modality_id:
            resources = await self._resource_repository.get_by_modality(
                modality_id=modality_id,
                resource_type=resource_type,
                skip=skip,
                limit=limit,
            )
        else:
            resources = await self._resource_repository.get_public(
                resource_type=resource_type,
                skip=skip,
                limit=limit,
            )

        return ResourceListDTO(
            resources=[ResourceDTO.from_entity(r) for r in resources],
            total=len(resources),
        )

    async def search(
        self,
        query: str,
        modality_id: UUID | None = None,
        resource_type: ResourceType | None = None,
        tags: list[str] | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ResourceListDTO:
        """Search resources."""
        resources = await self._resource_repository.search(
            query=query,
            modality_id=modality_id,
            resource_type=resource_type,
            tags=tags,
            skip=skip,
            limit=limit,
        )

        return ResourceListDTO(
            resources=[ResourceDTO.from_entity(r) for r in resources],
            total=len(resources),
        )

    async def get_popular(
        self,
        modality_id: UUID | None = None,
        limit: int = 10,
    ) -> ResourceListDTO:
        """Get popular resources."""
        resources = await self._resource_repository.get_popular(
            modality_id=modality_id,
            limit=limit,
        )

        return ResourceListDTO(
            resources=[ResourceDTO.from_entity(r) for r in resources],
            total=len(resources),
        )


class GetResourceUseCase:
    """Use case for getting a single resource."""

    def __init__(self, resource_repository: ResourceRepository) -> None:
        self._resource_repository = resource_repository

    async def execute(
        self,
        resource_id: UUID,
        user_modality_id: UUID | None = None,
        is_admin: bool = False,
        track_view: bool = True,
    ) -> ResourceDTO:
        """Get a resource by ID.

        Args:
            resource_id: Resource UUID.
            user_modality_id: User's modality for access check.
            is_admin: Whether user is admin.
            track_view: Whether to increment view count.

        Returns:
            Resource DTO.

        Raises:
            ResourceNotFoundException: If resource not found.
            ResourceAccessDeniedException: If access denied.
        """
        resource = await self._resource_repository.get_by_id(resource_id)
        if not resource:
            raise ResourceNotFoundException(str(resource_id))

        # Check access
        if not resource.can_access(user_modality_id, is_admin):
            raise ResourceAccessDeniedException(str(resource_id))

        # Track view
        if track_view:
            await self._resource_repository.increment_view_count(resource_id)

        return ResourceDTO.from_entity(resource)

    async def track_download(self, resource_id: UUID) -> bool:
        """Track a download for a resource."""
        return await self._resource_repository.increment_download_count(resource_id)
