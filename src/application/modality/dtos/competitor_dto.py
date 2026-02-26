"""Competitor DTOs."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.domain.modality.entities.competitor import Competitor


@dataclass(frozen=True)
class CompetitorDTO:
    """Competitor data transfer object."""

    id: UUID
    user_id: UUID
    full_name: str
    birth_date: date | None
    document_number: str | None
    phone: str | None
    emergency_contact: str | None
    emergency_phone: str | None
    notes: str | None
    is_active: bool
    age: int | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, competitor: Competitor) -> "CompetitorDTO":
        """Create DTO from Competitor entity."""
        return cls(
            id=competitor.id,
            user_id=competitor.user_id,
            full_name=competitor.full_name,
            birth_date=competitor.birth_date,
            document_number=competitor.document_number,
            phone=competitor.phone,
            emergency_contact=competitor.emergency_contact,
            emergency_phone=competitor.emergency_phone,
            notes=competitor.notes,
            is_active=competitor.is_active,
            age=competitor.age,
            created_at=competitor.created_at,
            updated_at=competitor.updated_at,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "full_name": self.full_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "document_number": self.document_number,
            "phone": self.phone,
            "emergency_contact": self.emergency_contact,
            "emergency_phone": self.emergency_phone,
            "notes": self.notes,
            "is_active": self.is_active,
            "age": self.age,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class CompetitorListDTO:
    """Competitor list DTO with pagination."""

    competitors: list[CompetitorDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more competitors."""
        return self.skip + len(self.competitors) < self.total


@dataclass(frozen=True)
class CreateCompetitorDTO:
    """DTO for creating a competitor."""

    user_id: UUID
    full_name: str
    birth_date: date | None = None
    document_number: str | None = None
    phone: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class UpdateCompetitorDTO:
    """DTO for updating a competitor."""

    full_name: str | None = None
    birth_date: date | None = None
    document_number: str | None = None
    phone: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    notes: str | None = None
    is_active: bool | None = None
