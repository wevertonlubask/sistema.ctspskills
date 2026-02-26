"""Resource entity for library management."""

from datetime import datetime
from uuid import UUID, uuid4

from src.shared.constants.enums import ResourceAccessLevel, ResourceType
from src.shared.domain.aggregate_root import AggregateRoot


class Resource(AggregateRoot[UUID]):
    """Resource entity for training materials library."""

    def __init__(
        self,
        title: str,
        resource_type: ResourceType,
        created_by: UUID,
        description: str | None = None,
        url: str | None = None,
        file_path: str | None = None,
        file_size: int | None = None,
        mime_type: str | None = None,
        modality_id: UUID | None = None,
        access_level: ResourceAccessLevel = ResourceAccessLevel.MODALITY,
        tags: list[str] | None = None,
        is_active: bool = True,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._title = title
        self._description = description
        self._resource_type = resource_type
        self._url = url
        self._file_path = file_path
        self._file_size = file_size
        self._mime_type = mime_type
        self._modality_id = modality_id
        self._access_level = access_level
        self._tags = tags or []
        self._is_active = is_active
        self._created_by = created_by
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._view_count = 0
        self._download_count = 0

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def resource_type(self) -> ResourceType:
        return self._resource_type

    @property
    def url(self) -> str | None:
        return self._url

    @property
    def file_path(self) -> str | None:
        return self._file_path

    @property
    def file_size(self) -> int | None:
        return self._file_size

    @property
    def mime_type(self) -> str | None:
        return self._mime_type

    @property
    def modality_id(self) -> UUID | None:
        return self._modality_id

    @property
    def access_level(self) -> ResourceAccessLevel:
        return self._access_level

    @property
    def tags(self) -> list[str]:
        return self._tags.copy()

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_by(self) -> UUID:
        return self._created_by

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def view_count(self) -> int:
        return self._view_count

    @property
    def download_count(self) -> int:
        return self._download_count

    @property
    def is_file(self) -> bool:
        """Check if resource is a file upload."""
        return self._file_path is not None

    @property
    def is_link(self) -> bool:
        """Check if resource is an external link."""
        return self._url is not None and self._file_path is None

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        access_level: ResourceAccessLevel | None = None,
    ) -> None:
        """Update resource details."""
        if title is not None:
            self._title = title
        if description is not None:
            self._description = description
        if url is not None:
            self._url = url
        if access_level is not None:
            self._access_level = access_level
        self._updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> bool:
        """Add a tag to the resource."""
        tag = tag.lower().strip()
        if tag and tag not in self._tags:
            self._tags.append(tag)
            self._updated_at = datetime.utcnow()
            return True
        return False

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the resource."""
        tag = tag.lower().strip()
        if tag in self._tags:
            self._tags.remove(tag)
            self._updated_at = datetime.utcnow()
            return True
        return False

    def increment_view(self) -> None:
        """Increment view count."""
        self._view_count += 1

    def increment_download(self) -> None:
        """Increment download count."""
        self._download_count += 1

    def deactivate(self) -> None:
        """Deactivate the resource."""
        self._is_active = False
        self._updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the resource."""
        self._is_active = True
        self._updated_at = datetime.utcnow()

    def can_access(self, user_modality_id: UUID | None, is_admin: bool = False) -> bool:
        """Check if user can access this resource."""
        if is_admin:
            return True
        if self._access_level == ResourceAccessLevel.PUBLIC:
            return True
        if self._access_level == ResourceAccessLevel.MODALITY:
            return self._modality_id == user_modality_id
        return False
