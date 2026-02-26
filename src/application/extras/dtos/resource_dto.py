"""Resource DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.extras.entities.resource import Resource
from src.shared.constants.enums import ResourceAccessLevel, ResourceType


@dataclass
class CreateResourceDTO:
    """DTO for creating a resource."""

    title: str
    resource_type: ResourceType
    description: str | None = None
    url: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    modality_id: UUID | None = None
    access_level: ResourceAccessLevel = ResourceAccessLevel.MODALITY
    tags: list[str] | None = None


@dataclass
class UpdateResourceDTO:
    """DTO for updating a resource."""

    title: str | None = None
    description: str | None = None
    url: str | None = None
    access_level: ResourceAccessLevel | None = None


@dataclass
class ResourceDTO:
    """DTO for resource responses."""

    id: UUID
    title: str
    description: str | None
    resource_type: str
    url: str | None
    file_path: str | None
    file_size: int | None
    mime_type: str | None
    modality_id: UUID | None
    access_level: str
    tags: list[str]
    is_active: bool
    view_count: int
    download_count: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: Resource) -> "ResourceDTO":
        return cls(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            resource_type=entity.resource_type.value,
            url=entity.url,
            file_path=entity.file_path,
            file_size=entity.file_size,
            mime_type=entity.mime_type,
            modality_id=entity.modality_id,
            access_level=entity.access_level.value,
            tags=entity.tags,
            is_active=entity.is_active,
            view_count=entity.view_count,
            download_count=entity.download_count,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass
class ResourceListDTO:
    """DTO for resource list."""

    resources: list[ResourceDTO]
    total: int
