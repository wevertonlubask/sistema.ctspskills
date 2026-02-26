"""Competitor entity."""

from datetime import date, datetime
from uuid import UUID

from src.shared.domain.aggregate_root import AggregateRoot


class Competitor(AggregateRoot[UUID]):
    """Competitor entity representing a person training for competitions.

    A competitor is linked to a User but contains competition-specific
    information like birth date, document numbers, and modality enrollments.
    """

    def __init__(
        self,
        user_id: UUID,
        full_name: str,
        birth_date: date | None = None,
        document_number: str | None = None,
        phone: str | None = None,
        emergency_contact: str | None = None,
        emergency_phone: str | None = None,
        notes: str | None = None,
        is_active: bool = True,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._user_id = user_id
        self._full_name = full_name.strip()
        self._birth_date = birth_date
        self._document_number = document_number
        self._phone = phone
        self._emergency_contact = emergency_contact
        self._emergency_phone = emergency_phone
        self._notes = notes
        self._is_active = is_active

    @property
    def user_id(self) -> UUID:
        """Get linked user ID."""
        return self._user_id

    @property
    def full_name(self) -> str:
        """Get competitor full name."""
        return self._full_name

    @property
    def birth_date(self) -> date | None:
        """Get birth date."""
        return self._birth_date

    @property
    def document_number(self) -> str | None:
        """Get document number (CPF/RG)."""
        return self._document_number

    @property
    def phone(self) -> str | None:
        """Get phone number."""
        return self._phone

    @property
    def emergency_contact(self) -> str | None:
        """Get emergency contact name."""
        return self._emergency_contact

    @property
    def emergency_phone(self) -> str | None:
        """Get emergency contact phone."""
        return self._emergency_phone

    @property
    def notes(self) -> str | None:
        """Get additional notes."""
        return self._notes

    @property
    def is_active(self) -> bool:
        """Check if competitor is active."""
        return self._is_active

    @property
    def age(self) -> int | None:
        """Calculate competitor age."""
        if not self._birth_date:
            return None
        today = date.today()
        age = today.year - self._birth_date.year
        if (today.month, today.day) < (self._birth_date.month, self._birth_date.day):
            age -= 1
        return age

    def update(
        self,
        full_name: str | None = None,
        birth_date: date | None = None,
        document_number: str | None = None,
        phone: str | None = None,
        emergency_contact: str | None = None,
        emergency_phone: str | None = None,
        notes: str | None = None,
    ) -> None:
        """Update competitor details."""
        if full_name is not None:
            self._full_name = full_name.strip()
        if birth_date is not None:
            self._birth_date = birth_date
        if document_number is not None:
            self._document_number = document_number
        if phone is not None:
            self._phone = phone
        if emergency_contact is not None:
            self._emergency_contact = emergency_contact
        if emergency_phone is not None:
            self._emergency_phone = emergency_phone
        if notes is not None:
            self._notes = notes
        self._touch()

    def activate(self) -> None:
        """Activate the competitor."""
        self._is_active = True
        self._touch()

    def deactivate(self) -> None:
        """Deactivate the competitor."""
        self._is_active = False
        self._touch()

    def __repr__(self) -> str:
        return f"Competitor(id={self._id}, name={self._full_name!r})"
