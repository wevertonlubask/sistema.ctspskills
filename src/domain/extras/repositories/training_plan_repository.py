"""Training plan repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.extras.entities.training_plan import PlanItem, TrainingPlan
from src.shared.constants.enums import TrainingPlanStatus


class TrainingPlanRepository(ABC):
    """Abstract repository for training plans."""

    @abstractmethod
    async def save(self, plan: TrainingPlan) -> TrainingPlan:
        """Save a training plan."""
        ...

    @abstractmethod
    async def get_by_id(self, plan_id: UUID) -> TrainingPlan | None:
        """Get training plan by ID."""
        ...

    @abstractmethod
    async def get_by_competitor(
        self,
        competitor_id: UUID,
        status: TrainingPlanStatus | None = None,
        modality_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[TrainingPlan]:
        """Get training plans for a competitor."""
        ...

    @abstractmethod
    async def get_active(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> list[TrainingPlan]:
        """Get active training plans."""
        ...

    @abstractmethod
    async def get_suggested(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> list[TrainingPlan]:
        """Get suggested training plans."""
        ...

    @abstractmethod
    async def get_overdue(
        self,
        competitor_id: UUID | None = None,
    ) -> list[TrainingPlan]:
        """Get overdue training plans."""
        ...

    @abstractmethod
    async def update(self, plan: TrainingPlan) -> TrainingPlan:
        """Update a training plan."""
        ...

    @abstractmethod
    async def delete(self, plan_id: UUID) -> bool:
        """Delete a training plan."""
        ...

    @abstractmethod
    async def save_item(self, item: PlanItem) -> PlanItem:
        """Save a plan item."""
        ...

    @abstractmethod
    async def get_item(self, item_id: UUID) -> PlanItem | None:
        """Get plan item by ID."""
        ...

    @abstractmethod
    async def get_items(self, plan_id: UUID) -> list[PlanItem]:
        """Get items for a plan."""
        ...

    @abstractmethod
    async def update_item(self, item: PlanItem) -> PlanItem:
        """Update a plan item."""
        ...

    @abstractmethod
    async def delete_item(self, item_id: UUID) -> bool:
        """Delete a plan item."""
        ...

    @abstractmethod
    async def reorder_items(self, plan_id: UUID, item_ids: list[UUID]) -> bool:
        """Reorder plan items."""
        ...
