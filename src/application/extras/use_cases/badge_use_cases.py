"""Badge and Achievement use cases."""

from uuid import UUID

from src.application.extras.dtos.badge_dto import (
    AchievementDTO,
    BadgeDTO,
    LeaderboardDTO,
    LeaderboardEntryDTO,
    UserPointsDTO,
)
from src.domain.extras.entities.badge import Achievement, UserPoints
from src.domain.extras.exceptions import (
    BadgeAlreadyEarnedException,
    BadgeNotFoundException,
)
from src.domain.extras.repositories.badge_repository import (
    AchievementRepository,
    BadgeRepository,
)
from src.shared.constants.enums import BadgeCategory, BadgeRarity


class AwardBadgeUseCase:
    """Use case for awarding badges to users."""

    def __init__(
        self,
        badge_repository: BadgeRepository,
        achievement_repository: AchievementRepository,
    ) -> None:
        self._badge_repository = badge_repository
        self._achievement_repository = achievement_repository

    async def execute(
        self,
        user_id: UUID,
        badge_id: UUID,
        competitor_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> AchievementDTO:
        """Award a badge to a user.

        Args:
            user_id: User UUID.
            badge_id: Badge UUID.
            competitor_id: Optional competitor UUID.
            metadata: Optional achievement metadata.

        Returns:
            Achievement DTO.

        Raises:
            BadgeNotFoundException: If badge not found.
            BadgeAlreadyEarnedException: If user already has badge.
        """
        # Check badge exists
        badge = await self._badge_repository.get_by_id(badge_id)
        if not badge:
            raise BadgeNotFoundException(str(badge_id))

        # Check if already earned
        if await self._achievement_repository.has_badge(user_id, badge_id):
            raise BadgeAlreadyEarnedException(str(badge_id), str(user_id))

        # Create achievement
        achievement = Achievement(
            badge_id=badge_id,
            user_id=user_id,
            competitor_id=competitor_id,
            metadata=metadata,
        )

        saved = await self._achievement_repository.save(achievement)

        # Update user points
        user_points = await self._achievement_repository.get_user_points(user_id)
        if not user_points:
            user_points = UserPoints(user_id=user_id)

        user_points.add_points(badge.points)
        user_points.increment_badges()
        await self._achievement_repository.save_user_points(user_points)

        return AchievementDTO.from_entity(saved, badge)


class ListBadgesUseCase:
    """Use case for listing badges."""

    def __init__(
        self,
        badge_repository: BadgeRepository,
        achievement_repository: AchievementRepository,
    ) -> None:
        self._badge_repository = badge_repository
        self._achievement_repository = achievement_repository

    async def execute(
        self,
        category: BadgeCategory | None = None,
        rarity: BadgeRarity | None = None,
    ) -> list[BadgeDTO]:
        """List all available badges.

        Args:
            category: Optional category filter.
            rarity: Optional rarity filter.

        Returns:
            List of badge DTOs.
        """
        badges = await self._badge_repository.get_all(
            category=category,
            rarity=rarity,
        )

        return [BadgeDTO.from_entity(b) for b in badges]

    async def get_user_achievements(
        self,
        user_id: UUID,
        include_in_progress: bool = False,
    ) -> list[AchievementDTO]:
        """Get achievements for a user.

        Args:
            user_id: User UUID.
            include_in_progress: Include incomplete achievements.

        Returns:
            List of achievement DTOs.
        """
        achievements = await self._achievement_repository.get_by_user(
            user_id=user_id,
            include_in_progress=include_in_progress,
        )

        # Get badges for achievements
        result = []
        for achievement in achievements:
            badge = await self._badge_repository.get_by_id(achievement.badge_id)
            result.append(AchievementDTO.from_entity(achievement, badge))

        return result

    async def get_user_points(self, user_id: UUID) -> UserPointsDTO:
        """Get user points.

        Args:
            user_id: User UUID.

        Returns:
            User points DTO.
        """
        user_points = await self._achievement_repository.get_user_points(user_id)
        if not user_points:
            user_points = UserPoints(user_id=user_id)

        return UserPointsDTO.from_entity(user_points)


class GetLeaderboardUseCase:
    """Use case for getting gamification leaderboard."""

    def __init__(
        self,
        achievement_repository: AchievementRepository,
    ) -> None:
        self._achievement_repository = achievement_repository

    async def execute(
        self,
        modality_id: UUID | None = None,
        limit: int = 50,
    ) -> LeaderboardDTO:
        """Get gamification leaderboard.

        Args:
            modality_id: Optional modality filter.
            limit: Maximum entries.

        Returns:
            Leaderboard DTO.
        """
        user_points_list = await self._achievement_repository.get_leaderboard(
            modality_id=modality_id,
            limit=limit,
        )

        entries = []
        for i, user_points in enumerate(user_points_list):
            entries.append(
                LeaderboardEntryDTO(
                    position=i + 1,
                    user_id=user_points.user_id,
                    user_name="",  # Would be populated from user repository
                    total_points=user_points.total_points,
                    level=user_points.level,
                    badges_count=user_points.badges_count,
                )
            )

        return LeaderboardDTO(
            entries=entries,
            total=len(entries),
        )
