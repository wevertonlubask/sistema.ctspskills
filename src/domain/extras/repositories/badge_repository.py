"""Badge and Achievement repository interfaces."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.extras.entities.badge import Achievement, Badge, UserPoints
from src.shared.constants.enums import BadgeCategory, BadgeRarity


class BadgeRepository(ABC):
    """Abstract repository for badges."""

    @abstractmethod
    async def save(self, badge: Badge) -> Badge:
        """Save a badge."""
        ...

    @abstractmethod
    async def get_by_id(self, badge_id: UUID) -> Badge | None:
        """Get badge by ID."""
        ...

    @abstractmethod
    async def get_all(
        self,
        category: BadgeCategory | None = None,
        rarity: BadgeRarity | None = None,
        is_active: bool = True,
    ) -> list[Badge]:
        """Get all badges with optional filters."""
        ...

    @abstractmethod
    async def get_by_category(
        self,
        category: BadgeCategory,
        is_active: bool = True,
    ) -> list[Badge]:
        """Get badges by category."""
        ...

    @abstractmethod
    async def update(self, badge: Badge) -> Badge:
        """Update a badge."""
        ...

    @abstractmethod
    async def delete(self, badge_id: UUID) -> bool:
        """Delete a badge."""
        ...


class AchievementRepository(ABC):
    """Abstract repository for achievements."""

    @abstractmethod
    async def save(self, achievement: Achievement) -> Achievement:
        """Save an achievement."""
        ...

    @abstractmethod
    async def get_by_id(self, achievement_id: UUID) -> Achievement | None:
        """Get achievement by ID."""
        ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        include_in_progress: bool = False,
    ) -> list[Achievement]:
        """Get achievements for a user."""
        ...

    @abstractmethod
    async def get_by_badge(
        self,
        badge_id: UUID,
        user_id: UUID | None = None,
    ) -> list[Achievement]:
        """Get achievements for a badge."""
        ...

    @abstractmethod
    async def has_badge(self, user_id: UUID, badge_id: UUID) -> bool:
        """Check if user has earned a specific badge."""
        ...

    @abstractmethod
    async def update(self, achievement: Achievement) -> Achievement:
        """Update an achievement."""
        ...

    @abstractmethod
    async def delete(self, achievement_id: UUID) -> bool:
        """Delete an achievement."""
        ...

    @abstractmethod
    async def get_user_points(self, user_id: UUID) -> UserPoints | None:
        """Get user points."""
        ...

    @abstractmethod
    async def save_user_points(self, user_points: UserPoints) -> UserPoints:
        """Save user points."""
        ...

    @abstractmethod
    async def get_leaderboard(
        self,
        modality_id: UUID | None = None,
        limit: int = 50,
    ) -> list[UserPoints]:
        """Get gamification leaderboard."""
        ...
