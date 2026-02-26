"""Goal use cases."""

from uuid import UUID

from src.application.extras.dtos.goal_dto import (
    CreateGoalDTO,
    GoalDTO,
    GoalListDTO,
    MilestoneDTO,
)
from src.domain.extras.entities.goal import Goal, Milestone
from src.domain.extras.exceptions import GoalNotFoundException, MilestoneNotFoundException
from src.domain.extras.repositories.goal_repository import GoalRepository
from src.shared.constants.enums import GoalStatus


class CreateGoalUseCase:
    """Use case for creating goals."""

    def __init__(self, goal_repository: GoalRepository) -> None:
        self._goal_repository = goal_repository

    async def execute(
        self,
        creator_id: UUID,
        dto: CreateGoalDTO,
    ) -> GoalDTO:
        """Create a goal.

        Args:
            creator_id: Creator user UUID.
            dto: Goal data.

        Returns:
            Created goal DTO.
        """
        goal = Goal(
            title=dto.title,
            competitor_id=dto.competitor_id,
            created_by=creator_id,
            description=dto.description,
            target_value=dto.target_value,
            unit=dto.unit,
            priority=dto.priority,
            start_date=dto.start_date,
            due_date=dto.due_date,
            modality_id=dto.modality_id,
            competence_id=dto.competence_id,
        )

        # Add milestones if provided
        if dto.milestones:
            for m_dto in dto.milestones:
                milestone = Milestone(
                    goal_id=goal.id,
                    title=m_dto.title,
                    target_value=m_dto.target_value,
                    due_date=m_dto.due_date,
                )
                goal.add_milestone(milestone)

        saved = await self._goal_repository.save(goal)
        return GoalDTO.from_entity(saved)


class ListGoalsUseCase:
    """Use case for listing goals."""

    def __init__(self, goal_repository: GoalRepository) -> None:
        self._goal_repository = goal_repository

    async def execute(
        self,
        competitor_id: UUID,
        status: GoalStatus | None = None,
        modality_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> GoalListDTO:
        """List goals for a competitor.

        Args:
            competitor_id: Competitor UUID.
            status: Optional status filter.
            modality_id: Optional modality filter.
            skip: Number of items to skip.
            limit: Maximum items to return.

        Returns:
            Goal list DTO.
        """
        goals = await self._goal_repository.get_by_competitor(
            competitor_id=competitor_id,
            status=status,
            modality_id=modality_id,
            skip=skip,
            limit=limit,
        )

        overdue = await self._goal_repository.get_overdue(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )

        return GoalListDTO(
            goals=[GoalDTO.from_entity(g) for g in goals],
            total=len(goals),
            overdue_count=len(overdue),
        )


class UpdateGoalProgressUseCase:
    """Use case for updating goal progress."""

    def __init__(self, goal_repository: GoalRepository) -> None:
        self._goal_repository = goal_repository

    async def execute(
        self,
        goal_id: UUID,
        current_value: float,
    ) -> GoalDTO:
        """Update goal progress.

        Args:
            goal_id: Goal UUID.
            current_value: New progress value.

        Returns:
            Updated goal DTO.

        Raises:
            GoalNotFoundException: If goal not found.
        """
        goal = await self._goal_repository.get_by_id(goal_id)
        if not goal:
            raise GoalNotFoundException(str(goal_id))

        goal.update_progress(current_value)
        saved = await self._goal_repository.update(goal)
        return GoalDTO.from_entity(saved)

    async def update_milestone(
        self,
        milestone_id: UUID,
        current_value: float,
    ) -> MilestoneDTO:
        """Update milestone progress.

        Args:
            milestone_id: Milestone UUID.
            current_value: New progress value.

        Returns:
            Updated milestone DTO.
        """
        milestone = await self._goal_repository.get_milestone(milestone_id)
        if not milestone:
            raise MilestoneNotFoundException(str(milestone_id))

        milestone.update_progress(current_value)
        saved = await self._goal_repository.update_milestone(milestone)
        return MilestoneDTO.from_entity(saved)

    async def complete_goal(self, goal_id: UUID) -> GoalDTO:
        """Mark goal as completed."""
        goal = await self._goal_repository.get_by_id(goal_id)
        if not goal:
            raise GoalNotFoundException(str(goal_id))

        goal.complete()
        saved = await self._goal_repository.update(goal)
        return GoalDTO.from_entity(saved)


class CheckGoalAlertsUseCase:
    """Use case for checking goals that need alerts (RN10)."""

    def __init__(self, goal_repository: GoalRepository) -> None:
        self._goal_repository = goal_repository

    async def execute(self, days_threshold: int = 7) -> list[GoalDTO]:
        """Get goals that need alerts.

        Args:
            days_threshold: Days threshold for upcoming deadlines.

        Returns:
            List of goals needing alerts.
        """
        goals = await self._goal_repository.get_needing_alert(
            days_threshold=days_threshold,
        )

        return [GoalDTO.from_entity(g) for g in goals]

    async def get_overdue(
        self,
        competitor_id: UUID | None = None,
        modality_id: UUID | None = None,
    ) -> list[GoalDTO]:
        """Get overdue goals."""
        goals = await self._goal_repository.get_overdue(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )

        return [GoalDTO.from_entity(g) for g in goals]
