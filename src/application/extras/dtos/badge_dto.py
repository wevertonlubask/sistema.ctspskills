"""Badge and Achievement DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.extras.entities.badge import Achievement, Badge, UserPoints
from src.shared.constants.enums import BadgeCategory, BadgeRarity


@dataclass
class CreateBadgeDTO:
    """DTO for creating a badge."""

    name: str
    description: str
    category: BadgeCategory
    rarity: BadgeRarity = BadgeRarity.COMMON
    icon_url: str | None = None
    points: int = 10
    criteria: dict | None = None


@dataclass
class BadgeDTO:
    """DTO for badge responses."""

    id: UUID
    name: str
    description: str
    category: str
    rarity: str
    icon_url: str | None
    points: int
    criteria: dict
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, entity: Badge) -> "BadgeDTO":
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            category=entity.category.value,
            rarity=entity.rarity.value,
            icon_url=entity.icon_url,
            points=entity.points,
            criteria=entity.criteria,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )


@dataclass
class AchievementDTO:
    """DTO for achievement responses."""

    id: UUID
    badge_id: UUID
    user_id: UUID
    competitor_id: UUID | None
    earned_at: datetime
    progress: float
    is_complete: bool
    metadata: dict
    badge: BadgeDTO | None = None

    @classmethod
    def from_entity(cls, entity: Achievement, badge: Badge | None = None) -> "AchievementDTO":
        return cls(
            id=entity.id,
            badge_id=entity.badge_id,
            user_id=entity.user_id,
            competitor_id=entity.competitor_id,
            earned_at=entity.earned_at,
            progress=entity.progress,
            is_complete=entity.is_complete,
            metadata=entity.metadata,
            badge=BadgeDTO.from_entity(badge) if badge else None,
        )


@dataclass
class UserPointsDTO:
    """DTO for user points."""

    user_id: UUID
    total_points: int
    level: int
    badges_count: int
    points_to_next_level: int

    @classmethod
    def from_entity(cls, entity: UserPoints) -> "UserPointsDTO":
        return cls(
            user_id=entity.user_id,
            total_points=entity.total_points,
            level=entity.level,
            badges_count=entity.badges_count,
            points_to_next_level=entity.points_to_next_level,
        )


@dataclass
class LeaderboardEntryDTO:
    """DTO for leaderboard entry."""

    position: int
    user_id: UUID
    user_name: str
    total_points: int
    level: int
    badges_count: int


@dataclass
class LeaderboardDTO:
    """DTO for leaderboard."""

    entries: list[LeaderboardEntryDTO]
    total: int
