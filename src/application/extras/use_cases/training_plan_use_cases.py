"""Training Plan use cases."""

from uuid import UUID

from src.application.extras.dtos.training_plan_dto import (
    CreatePlanDTO,
    PlanItemDTO,
    TrainingPlanDTO,
    TrainingPlanListDTO,
)
from src.domain.extras.entities.training_plan import PlanItem, TrainingPlan
from src.domain.extras.exceptions import (
    PlanItemNotFoundException,
    TrainingPlanNotFoundException,
)
from src.domain.extras.repositories.training_plan_repository import TrainingPlanRepository
from src.shared.constants.enums import TrainingPlanStatus


class CreateTrainingPlanUseCase:
    """Use case for creating training plans."""

    def __init__(self, plan_repository: TrainingPlanRepository) -> None:
        self._plan_repository = plan_repository

    async def execute(
        self,
        creator_id: UUID,
        dto: CreatePlanDTO,
    ) -> TrainingPlanDTO:
        """Create a training plan.

        Args:
            creator_id: Creator user UUID.
            dto: Plan data.

        Returns:
            Created plan DTO.
        """
        plan = TrainingPlan(
            title=dto.title,
            competitor_id=dto.competitor_id,
            created_by=creator_id,
            description=dto.description,
            modality_id=dto.modality_id,
            priority=dto.priority,
            start_date=dto.start_date,
            end_date=dto.end_date,
            target_hours=dto.target_hours,
        )

        # Add items if provided
        if dto.items:
            for i, item_dto in enumerate(dto.items):
                item = PlanItem(
                    plan_id=plan.id,
                    title=item_dto.title,
                    description=item_dto.description,
                    competence_id=item_dto.competence_id,
                    order=i + 1,
                    duration_hours=item_dto.duration_hours,
                    is_required=item_dto.is_required,
                    due_date=item_dto.due_date,
                    notes=item_dto.notes,
                    resource_ids=item_dto.resource_ids,
                )
                plan.add_item(item)

        saved = await self._plan_repository.save(plan)
        return TrainingPlanDTO.from_entity(saved)

    async def create_suggested(
        self,
        creator_id: UUID,
        competitor_id: UUID,
        modality_id: UUID,
        title: str,
        description: str | None = None,
    ) -> TrainingPlanDTO:
        """Create a suggested training plan."""
        plan = TrainingPlan.create_suggested_plan(
            title=title,
            competitor_id=competitor_id,
            created_by=creator_id,
            modality_id=modality_id,
            description=description,
        )

        saved = await self._plan_repository.save(plan)
        return TrainingPlanDTO.from_entity(saved)


class ListTrainingPlansUseCase:
    """Use case for listing training plans."""

    def __init__(self, plan_repository: TrainingPlanRepository) -> None:
        self._plan_repository = plan_repository

    async def execute(
        self,
        competitor_id: UUID,
        status: TrainingPlanStatus | None = None,
        modality_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> TrainingPlanListDTO:
        """List training plans for a competitor.

        Args:
            competitor_id: Competitor UUID.
            status: Optional status filter.
            modality_id: Optional modality filter.
            skip: Number of items to skip.
            limit: Maximum items to return.

        Returns:
            Training plan list DTO.
        """
        plans = await self._plan_repository.get_by_competitor(
            competitor_id=competitor_id,
            status=status,
            modality_id=modality_id,
            skip=skip,
            limit=limit,
        )

        active_plans = await self._plan_repository.get_active(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )

        return TrainingPlanListDTO(
            plans=[TrainingPlanDTO.from_entity(p) for p in plans],
            total=len(plans),
            active_count=len(active_plans),
        )

    async def get_suggested(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> list[TrainingPlanDTO]:
        """Get suggested training plans."""
        plans = await self._plan_repository.get_suggested(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )

        return [TrainingPlanDTO.from_entity(p) for p in plans]


class UpdatePlanProgressUseCase:
    """Use case for updating training plan progress."""

    def __init__(self, plan_repository: TrainingPlanRepository) -> None:
        self._plan_repository = plan_repository

    async def complete_item(
        self,
        item_id: UUID,
    ) -> PlanItemDTO:
        """Mark a plan item as completed.

        Args:
            item_id: Plan item UUID.

        Returns:
            Updated item DTO.

        Raises:
            PlanItemNotFoundException: If item not found.
        """
        item = await self._plan_repository.get_item(item_id)
        if not item:
            raise PlanItemNotFoundException(str(item_id))

        item.complete()
        saved = await self._plan_repository.update_item(item)
        return PlanItemDTO.from_entity(saved)

    async def activate_plan(self, plan_id: UUID) -> TrainingPlanDTO:
        """Activate a training plan.

        Args:
            plan_id: Plan UUID.

        Returns:
            Updated plan DTO.
        """
        plan = await self._plan_repository.get_by_id(plan_id)
        if not plan:
            raise TrainingPlanNotFoundException(str(plan_id))

        plan.activate()
        saved = await self._plan_repository.update(plan)
        return TrainingPlanDTO.from_entity(saved)

    async def complete_plan(self, plan_id: UUID) -> TrainingPlanDTO:
        """Mark a training plan as completed.

        Args:
            plan_id: Plan UUID.

        Returns:
            Updated plan DTO.
        """
        plan = await self._plan_repository.get_by_id(plan_id)
        if not plan:
            raise TrainingPlanNotFoundException(str(plan_id))

        plan.complete()
        saved = await self._plan_repository.update(plan)
        return TrainingPlanDTO.from_entity(saved)

    async def add_item(
        self,
        plan_id: UUID,
        title: str,
        description: str | None = None,
        competence_id: UUID | None = None,
        duration_hours: float = 1.0,
        is_required: bool = True,
    ) -> TrainingPlanDTO:
        """Add an item to a training plan.

        Args:
            plan_id: Plan UUID.
            title: Item title.
            description: Item description.
            competence_id: Optional competence UUID.
            duration_hours: Duration in hours.
            is_required: Whether item is required.

        Returns:
            Updated plan DTO.
        """
        plan = await self._plan_repository.get_by_id(plan_id)
        if not plan:
            raise TrainingPlanNotFoundException(str(plan_id))

        item = PlanItem(
            plan_id=plan_id,
            title=title,
            description=description,
            competence_id=competence_id,
            duration_hours=duration_hours,
            is_required=is_required,
        )

        plan.add_item(item)
        saved = await self._plan_repository.update(plan)
        return TrainingPlanDTO.from_entity(saved)

    async def reorder_items(
        self,
        plan_id: UUID,
        item_ids: list[UUID],
    ) -> TrainingPlanDTO:
        """Reorder items in a training plan.

        Args:
            plan_id: Plan UUID.
            item_ids: Ordered list of item UUIDs.

        Returns:
            Updated plan DTO.
        """
        plan = await self._plan_repository.get_by_id(plan_id)
        if not plan:
            raise TrainingPlanNotFoundException(str(plan_id))

        await self._plan_repository.reorder_items(plan_id, item_ids)

        # Reload plan
        plan = await self._plan_repository.get_by_id(plan_id)
        if not plan:
            raise TrainingPlanNotFoundException(str(plan_id))
        return TrainingPlanDTO.from_entity(plan)
