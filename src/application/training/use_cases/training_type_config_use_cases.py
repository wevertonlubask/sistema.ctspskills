"""Training type config use cases."""

from uuid import UUID

from src.application.training.dtos.training_type_config_dto import (
    TrainingTypeConfigDTO,
    TrainingTypeConfigListDTO,
)
from src.domain.training.entities.training_type_config import TrainingTypeConfig
from src.domain.training.repositories.training_type_config_repository import (
    TrainingTypeConfigRepository,
)


class CreateTrainingTypeConfigUseCase:
    """Use case for creating a new training type configuration."""

    def __init__(self, repository: TrainingTypeConfigRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        code: str,
        name: str,
        description: str | None = None,
        display_order: int = 0,
    ) -> TrainingTypeConfigDTO:
        """Create a new training type configuration.

        Args:
            code: Unique code for the training type (e.g., 'senai', 'external').
            name: Display name for the training type.
            description: Optional description.
            display_order: Order for display in UI.

        Returns:
            Created training type config DTO.

        Raises:
            ValueError: If code already exists.
        """
        # Check if code already exists
        if await self._repository.code_exists(code.lower()):
            raise ValueError(f"Training type with code '{code}' already exists")

        # Create entity
        entity = TrainingTypeConfig(
            code=code,
            name=name,
            description=description,
            display_order=display_order,
        )

        # Save
        saved = await self._repository.add(entity)
        return TrainingTypeConfigDTO.from_entity(saved)


class UpdateTrainingTypeConfigUseCase:
    """Use case for updating a training type configuration."""

    def __init__(self, repository: TrainingTypeConfigRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        id: UUID,
        name: str | None = None,
        description: str | None = None,
        display_order: int | None = None,
        is_active: bool | None = None,
    ) -> TrainingTypeConfigDTO:
        """Update a training type configuration.

        Args:
            id: Training type config ID.
            name: New display name.
            description: New description.
            display_order: New display order.
            is_active: Whether the type is active.

        Returns:
            Updated training type config DTO.

        Raises:
            ValueError: If training type not found.
        """
        # Get existing entity
        entity = await self._repository.get_by_id(id)
        if not entity:
            raise ValueError(f"Training type with id '{id}' not found")

        # Update fields
        entity.update(
            name=name,
            description=description,
            display_order=display_order,
        )

        if is_active is not None:
            if is_active:
                entity.activate()
            else:
                entity.deactivate()

        # Save
        saved = await self._repository.update(entity)
        return TrainingTypeConfigDTO.from_entity(saved)


class ListTrainingTypeConfigsUseCase:
    """Use case for listing training type configurations."""

    def __init__(self, repository: TrainingTypeConfigRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> TrainingTypeConfigListDTO:
        """List training type configurations.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            active_only: If True, return only active types.

        Returns:
            List of training type config DTOs.
        """
        items = await self._repository.get_all(
            skip=skip,
            limit=limit,
            active_only=active_only,
        )
        total = await self._repository.count(active_only=active_only)

        return TrainingTypeConfigListDTO(
            items=[TrainingTypeConfigDTO.from_entity(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
        )


class GetTrainingTypeConfigUseCase:
    """Use case for getting a single training type configuration."""

    def __init__(self, repository: TrainingTypeConfigRepository) -> None:
        self._repository = repository

    async def execute(self, id: UUID) -> TrainingTypeConfigDTO | None:
        """Get a training type configuration by ID.

        Args:
            id: Training type config ID.

        Returns:
            Training type config DTO if found, None otherwise.
        """
        entity = await self._repository.get_by_id(id)
        return TrainingTypeConfigDTO.from_entity(entity) if entity else None


class DeleteTrainingTypeConfigUseCase:
    """Use case for deleting a training type configuration."""

    def __init__(self, repository: TrainingTypeConfigRepository) -> None:
        self._repository = repository

    async def execute(self, id: UUID) -> bool:
        """Delete a training type configuration.

        Args:
            id: Training type config ID.

        Returns:
            True if deleted, False if not found.
        """
        return await self._repository.delete(id)
