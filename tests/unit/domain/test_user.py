"""Unit tests for User entity."""

from uuid import uuid4

import pytest

from src.domain.identity.entities.user import User
from src.domain.identity.exceptions import UserInactiveException
from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.password import Password
from src.shared.constants.enums import UserRole, UserStatus
from src.shared.exceptions import InvalidValueException


class TestEmail:
    """Tests for Email value object."""

    def test_create_valid_email(self):
        """Test creating a valid email."""
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    def test_email_normalized_to_lowercase(self):
        """Test that email is normalized to lowercase."""
        email = Email("TEST@EXAMPLE.COM")
        assert email.value == "test@example.com"

    def test_email_trimmed(self):
        """Test that email is trimmed."""
        email = Email("  test@example.com  ")
        assert email.value == "test@example.com"

    def test_email_domain_property(self):
        """Test email domain property."""
        email = Email("test@example.com")
        assert email.domain == "example.com"

    def test_email_local_part_property(self):
        """Test email local part property."""
        email = Email("test@example.com")
        assert email.local_part == "test"

    def test_invalid_email_raises_exception(self):
        """Test that invalid email raises exception."""
        with pytest.raises(InvalidValueException) as exc_info:
            Email("invalid-email")
        assert "email" in str(exc_info.value)

    def test_empty_email_raises_exception(self):
        """Test that empty email raises exception."""
        with pytest.raises(InvalidValueException):
            Email("")

    def test_email_equality(self):
        """Test email equality comparison."""
        email1 = Email("test@example.com")
        email2 = Email("TEST@example.com")
        assert email1 == email2


class TestPassword:
    """Tests for Password value object."""

    def test_create_password_from_hash(self):
        """Test creating password from hash."""
        password = Password("$2b$12$somehash")
        assert password.hashed_value == "$2b$12$somehash"

    def test_password_string_protected(self):
        """Test that password string is protected."""
        password = Password("$2b$12$somehash")
        assert str(password) == "[PROTECTED]"

    def test_empty_hash_raises_exception(self):
        """Test that empty hash raises exception."""
        with pytest.raises(InvalidValueException):
            Password("")

    def test_validate_raw_weak_password(self):
        """Test validation of weak password."""
        with pytest.raises(InvalidValueException):
            Password.validate_raw("weak")

    def test_validate_raw_no_uppercase(self):
        """Test validation of password without uppercase."""
        with pytest.raises(InvalidValueException):
            Password.validate_raw("password123!")

    def test_validate_raw_no_digit(self):
        """Test validation of password without digit."""
        with pytest.raises(InvalidValueException):
            Password.validate_raw("Password!")

    def test_validate_raw_no_special(self):
        """Test validation of password without special character."""
        with pytest.raises(InvalidValueException):
            Password.validate_raw("Password123")

    def test_validate_raw_valid_password(self):
        """Test validation of valid password."""
        # Should not raise
        Password.validate_raw("SecurePass123!")


class TestUser:
    """Tests for User entity."""

    @pytest.fixture
    def valid_user(self):
        """Create a valid user for testing."""
        return User(
            id=uuid4(),
            email=Email("test@example.com"),
            password=Password("$2b$12$somehash"),
            full_name="Test User",
            role=UserRole.COMPETITOR,
            status=UserStatus.ACTIVE,
        )

    def test_create_user(self, valid_user):
        """Test creating a user."""
        assert valid_user.email.value == "test@example.com"
        assert valid_user.full_name == "Test User"
        assert valid_user.role == UserRole.COMPETITOR
        assert valid_user.status == UserStatus.ACTIVE

    def test_user_is_active(self, valid_user):
        """Test is_active property."""
        assert valid_user.is_active is True

    def test_user_is_competitor(self, valid_user):
        """Test is_competitor property."""
        assert valid_user.is_competitor is True
        assert valid_user.is_evaluator is False
        assert valid_user.is_super_admin is False

    def test_user_deactivate(self, valid_user):
        """Test deactivating user."""
        valid_user.deactivate()
        assert valid_user.is_active is False
        assert valid_user.status == UserStatus.INACTIVE

    def test_user_activate(self, valid_user):
        """Test activating user."""
        valid_user.deactivate()
        valid_user.activate()
        assert valid_user.is_active is True

    def test_user_suspend(self, valid_user):
        """Test suspending user."""
        valid_user.suspend()
        assert valid_user.status == UserStatus.SUSPENDED

    def test_user_change_role(self, valid_user):
        """Test changing user role."""
        valid_user.change_role(UserRole.EVALUATOR)
        assert valid_user.role == UserRole.EVALUATOR
        assert valid_user.is_evaluator is True

    def test_user_update_full_name(self, valid_user):
        """Test updating full name."""
        valid_user.update_full_name("New Name")
        assert valid_user.full_name == "New Name"

    def test_ensure_active_raises_when_inactive(self, valid_user):
        """Test ensure_active raises exception when user is inactive."""
        valid_user.deactivate()
        with pytest.raises(UserInactiveException):
            valid_user.ensure_active()

    def test_super_admin_has_all_permissions(self):
        """Test that super admin has all permissions."""
        admin = User(
            email=Email("admin@example.com"),
            password=Password("$2b$12$hash"),
            full_name="Admin",
            role=UserRole.SUPER_ADMIN,
        )
        assert admin.has_permission("any:permission") is True

    def test_user_equality_by_id(self):
        """Test that users are equal by ID."""
        user_id = uuid4()
        user1 = User(
            id=user_id,
            email=Email("test1@example.com"),
            password=Password("$2b$12$hash"),
            full_name="User 1",
        )
        user2 = User(
            id=user_id,
            email=Email("test2@example.com"),
            password=Password("$2b$12$hash"),
            full_name="User 2",
        )
        assert user1 == user2

    def test_user_can_manage_role(self):
        """Test can_manage_role method."""
        admin = User(
            email=Email("admin@example.com"),
            password=Password("$2b$12$hash"),
            full_name="Admin",
            role=UserRole.SUPER_ADMIN,
        )
        assert admin.can_manage_role(UserRole.EVALUATOR) is True
        assert admin.can_manage_role(UserRole.COMPETITOR) is True
