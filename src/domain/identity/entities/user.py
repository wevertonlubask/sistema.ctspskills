"""User entity - Aggregate Root for Identity context."""

from datetime import datetime
from uuid import UUID

from src.domain.identity.entities.role import Role
from src.domain.identity.exceptions import (
    UserInactiveException,
)
from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.password import Password
from src.shared.constants.enums import UserRole, UserStatus
from src.shared.domain.aggregate_root import AggregateRoot


class User(AggregateRoot[UUID]):
    """User aggregate root.

    Represents a user in the system with their authentication credentials
    and role-based access control.
    """

    def __init__(
        self,
        email: Email,
        password: Password,
        full_name: str,
        role: UserRole = UserRole.COMPETITOR,
        status: UserStatus = UserStatus.ACTIVE,
        role_entity: Role | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        last_login_at: datetime | None = None,
        must_change_password: bool = False,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._email = email
        self._password = password
        self._full_name = full_name
        self._role = role
        self._status = status
        self._role_entity = role_entity
        self._last_login_at = last_login_at
        self._must_change_password = must_change_password

    @property
    def email(self) -> Email:
        """Get user email."""
        return self._email

    @property
    def password(self) -> Password:
        """Get user password (hashed)."""
        return self._password

    @property
    def full_name(self) -> str:
        """Get user full name."""
        return self._full_name

    @property
    def role(self) -> UserRole:
        """Get user role."""
        return self._role

    @property
    def status(self) -> UserStatus:
        """Get user status."""
        return self._status

    @property
    def role_entity(self) -> Role | None:
        """Get role entity with permissions."""
        return self._role_entity

    @property
    def last_login_at(self) -> datetime | None:
        """Get last login timestamp."""
        return self._last_login_at

    @property
    def must_change_password(self) -> bool:
        """Check if user must change password on next login."""
        return self._must_change_password

    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self._status == UserStatus.ACTIVE

    @property
    def is_super_admin(self) -> bool:
        """Check if user is super admin."""
        return self._role == UserRole.SUPER_ADMIN

    @property
    def is_evaluator(self) -> bool:
        """Check if user is evaluator."""
        return self._role == UserRole.EVALUATOR

    @property
    def is_competitor(self) -> bool:
        """Check if user is competitor."""
        return self._role == UserRole.COMPETITOR

    def update_email(self, new_email: Email) -> None:
        """Update user email.

        Args:
            new_email: New email value object.
        """
        self._email = new_email
        self._touch()

    def update_password(self, new_password: Password) -> None:
        """Update user password.

        Args:
            new_password: New password value object (already hashed).
        """
        self._password = new_password
        self._must_change_password = False  # Clear flag when password is changed
        self._touch()

    def require_password_change(self) -> None:
        """Mark user as needing to change password on next login."""
        self._must_change_password = True
        self._touch()

    def update_full_name(self, full_name: str) -> None:
        """Update user full name.

        Args:
            full_name: New full name.
        """
        self._full_name = full_name.strip()
        self._touch()

    def change_role(self, new_role: UserRole) -> None:
        """Change user role.

        Args:
            new_role: New role to assign.
        """
        self._role = new_role
        self._touch()

    def activate(self) -> None:
        """Activate user account."""
        self._status = UserStatus.ACTIVE
        self._touch()

    def deactivate(self) -> None:
        """Deactivate user account."""
        self._status = UserStatus.INACTIVE
        self._touch()

    def suspend(self) -> None:
        """Suspend user account."""
        self._status = UserStatus.SUSPENDED
        self._touch()

    def record_login(self, login_time: datetime) -> None:
        """Record successful login.

        Args:
            login_time: Timestamp of the login.
        """
        self._last_login_at = login_time
        self._touch()

    def ensure_active(self) -> None:
        """Ensure user is active.

        Raises:
            UserInactiveException: If user is not active.
        """
        if not self.is_active:
            raise UserInactiveException(
                user_id=str(self._id),
                status=self._status.value,
            )

    def has_permission(self, permission_code: str) -> bool:
        """Check if user has a specific permission.

        Args:
            permission_code: Permission code in format 'resource:action'.

        Returns:
            True if user has the permission (either through role or super admin).
        """
        # Super admin has all permissions
        if self.is_super_admin:
            return True

        # Check role permissions
        if self._role_entity:
            return self._role_entity.has_permission(permission_code)

        return False

    def can_manage_role(self, target_role: UserRole) -> bool:
        """Check if user can manage users with a specific role.

        Args:
            target_role: Role to check management permission for.

        Returns:
            True if user can manage the target role.
        """
        return self._role.has_permission_over(target_role)

    def __repr__(self) -> str:
        return f"User(id={self._id}, email={self._email}, role={self._role.value})"
