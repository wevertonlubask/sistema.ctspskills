"""Badge and Achievement entities for gamification."""

from datetime import datetime
from uuid import UUID, uuid4

from src.shared.constants.enums import BadgeCategory, BadgeRarity
from src.shared.domain.aggregate_root import AggregateRoot
from src.shared.domain.entity import Entity


class Badge(AggregateRoot[UUID]):
    """Badge entity for gamification rewards."""

    def __init__(
        self,
        name: str,
        description: str,
        category: BadgeCategory,
        rarity: BadgeRarity = BadgeRarity.COMMON,
        icon_url: str | None = None,
        points: int = 10,
        criteria: dict | None = None,
        is_active: bool = True,
        id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._name = name
        self._description = description
        self._category = category
        self._rarity = rarity
        self._icon_url = icon_url
        self._points = points
        self._criteria = criteria or {}
        self._is_active = is_active
        self._created_at = created_at or datetime.utcnow()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def category(self) -> BadgeCategory:
        return self._category

    @property
    def rarity(self) -> BadgeRarity:
        return self._rarity

    @property
    def icon_url(self) -> str | None:
        return self._icon_url

    @property
    def points(self) -> int:
        return self._points

    @property
    def criteria(self) -> dict:
        return self._criteria.copy()

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        icon_url: str | None = None,
        points: int | None = None,
    ) -> None:
        """Update badge details."""
        if name is not None:
            self._name = name
        if description is not None:
            self._description = description
        if icon_url is not None:
            self._icon_url = icon_url
        if points is not None:
            self._points = points

    def deactivate(self) -> None:
        """Deactivate the badge."""
        self._is_active = False

    def activate(self) -> None:
        """Activate the badge."""
        self._is_active = True

    @classmethod
    def create_training_badge(
        cls,
        name: str,
        description: str,
        hours_required: int,
        rarity: BadgeRarity = BadgeRarity.COMMON,
    ) -> "Badge":
        """Create a training hours badge."""
        return cls(
            name=name,
            description=description,
            category=BadgeCategory.TRAINING,
            rarity=rarity,
            criteria={"type": "training_hours", "hours_required": hours_required},
            points=hours_required,
        )

    @classmethod
    def create_performance_badge(
        cls,
        name: str,
        description: str,
        score_required: float,
        rarity: BadgeRarity = BadgeRarity.UNCOMMON,
    ) -> "Badge":
        """Create a performance badge."""
        return cls(
            name=name,
            description=description,
            category=BadgeCategory.PERFORMANCE,
            rarity=rarity,
            criteria={"type": "grade_average", "score_required": score_required},
            points=int(score_required),
        )

    @classmethod
    def create_consistency_badge(
        cls,
        name: str,
        description: str,
        days_streak: int,
        rarity: BadgeRarity = BadgeRarity.RARE,
    ) -> "Badge":
        """Create a consistency streak badge."""
        return cls(
            name=name,
            description=description,
            category=BadgeCategory.CONSISTENCY,
            rarity=rarity,
            criteria={"type": "training_streak", "days_required": days_streak},
            points=days_streak * 2,
        )


class Achievement(Entity[UUID]):
    """Achievement entity - badge awarded to a user."""

    def __init__(
        self,
        badge_id: UUID,
        user_id: UUID,
        competitor_id: UUID | None = None,
        earned_at: datetime | None = None,
        progress: float = 100.0,
        metadata: dict | None = None,
        id: UUID | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._badge_id = badge_id
        self._user_id = user_id
        self._competitor_id = competitor_id
        self._earned_at = earned_at or datetime.utcnow()
        self._progress = progress
        self._metadata = metadata or {}

    @property
    def badge_id(self) -> UUID:
        return self._badge_id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def competitor_id(self) -> UUID | None:
        return self._competitor_id

    @property
    def earned_at(self) -> datetime:
        return self._earned_at

    @property
    def progress(self) -> float:
        return self._progress

    @property
    def metadata(self) -> dict:
        return self._metadata.copy()

    @property
    def is_complete(self) -> bool:
        """Check if achievement is complete."""
        return self._progress >= 100.0

    def update_progress(self, progress: float) -> None:
        """Update achievement progress."""
        self._progress = min(100.0, progress)
        if self._progress >= 100.0:
            self._earned_at = datetime.utcnow()


class UserPoints(Entity[UUID]):
    """User points tracking for gamification."""

    def __init__(
        self,
        user_id: UUID,
        total_points: int = 0,
        level: int = 1,
        badges_count: int = 0,
        id: UUID | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._user_id = user_id
        self._total_points = total_points
        self._level = level
        self._badges_count = badges_count

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def total_points(self) -> int:
        return self._total_points

    @property
    def level(self) -> int:
        return self._level

    @property
    def badges_count(self) -> int:
        return self._badges_count

    @property
    def points_to_next_level(self) -> int:
        """Calculate points needed for next level."""
        # Level formula: level * 100 points per level
        next_level_threshold = self._level * 100
        return max(0, next_level_threshold - (self._total_points % 100))

    def add_points(self, points: int) -> bool:
        """Add points and return True if leveled up."""
        old_level = self._level
        self._total_points += points
        self._level = (self._total_points // 100) + 1
        return self._level > old_level

    def increment_badges(self) -> None:
        """Increment badge count."""
        self._badges_count += 1
