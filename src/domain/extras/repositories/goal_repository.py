"""Goal repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.extras.entities.goal import Goal, Milestone
from src.shared.constants.enums import GoalStatus


class GoalRepository(ABC):
    """Abstract repository for goals."""

    @abstractmethod
    async def save(self, goal: Goal) -> Goal:
        """Save a goal."""
        ...

    @abstractmethod
    async def get_by_id(self, goal_id: UUID) -> Goal | None:
        """Get goal by ID."""
        ...

    @abstractmethod
    async def get_by_competitor(
        self,
        competitor_id: UUID,
        status: GoalStatus | None = None,
        modality_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Goal]:
        """Get goals for a competitor."""
        ...

    @abstractmethod
    async def get_active(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> list[Goal]:
        """Get active (in progress) goals."""
        ...

    @abstractmethod
    async def get_overdue(
        self,
        competitor_id: UUID | None = None,
        modality_id: UUID | None = None,
    ) -> list[Goal]:
        """Get overdue goals (RN10)."""
        ...

    @abstractmethod
    async def get_needing_alert(
        self,
        days_threshold: int = 7,
    ) -> list[Goal]:
        """Get goals needing alerts (RN10)."""
        ...

    @abstractmethod
    async def update(self, goal: Goal) -> Goal:
        """Update a goal."""
        ...

    @abstractmethod
    async def delete(self, goal_id: UUID) -> bool:
        """Delete a goal."""
        ...

    @abstractmethod
    async def save_milestone(self, milestone: Milestone) -> Milestone:
        """Save a milestone."""
        ...

    @abstractmethod
    async def get_milestone(self, milestone_id: UUID) -> Milestone | None:
        """Get milestone by ID."""
        ...

    @abstractmethod
    async def get_milestones(self, goal_id: UUID) -> list[Milestone]:
        """Get milestones for a goal."""
        ...

    @abstractmethod
    async def update_milestone(self, milestone: Milestone) -> Milestone:
        """Update a milestone."""
        ...

    @abstractmethod
    async def delete_milestone(self, milestone_id: UUID) -> bool:
        """Delete a milestone."""
        ...
