"""Unit tests for RegisterUserUseCase."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.identity.dtos.auth_dto import RegisterUserDTO
from src.application.identity.use_cases.register_user import RegisterUserUseCase
from src.domain.identity.entities.user import User
from src.domain.identity.exceptions import UserAlreadyExistsException
from src.domain.identity.repositories.user_repository import UserRepository
from src.domain.identity.services.password_service import PasswordService
from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.password import Password
from src.shared.constants.enums import UserRole, UserStatus
from src.shared.exceptions import InvalidValueException


class TestRegisterUserUseCase:
    """Tests for RegisterUserUseCase."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository."""
        repo = AsyncMock(spec=UserRepository)
        repo.email_exists.return_value = False
        repo.add.return_value = User(
            id=uuid4(),
            email=Email("test@example.com"),
            password=Password("$2b$12$hashedpassword"),
            full_name="Test User",
            role=UserRole.COMPETITOR,
            status=UserStatus.ACTIVE,
        )
        return repo

    @pytest.fixture
    def mock_password_service(self):
        """Create mock password service."""
        service = MagicMock(spec=PasswordService)
        service.hash_password.return_value = "$2b$12$hashedpassword"
        return service

    @pytest.fixture
    def use_case(self, mock_user_repository, mock_password_service):
        """Create use case with mocks."""
        return RegisterUserUseCase(
            user_repository=mock_user_repository,
            password_service=mock_password_service,
        )

    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        use_case,
        mock_user_repository,
        mock_password_service,
    ):
        """Test successful user registration."""
        dto = RegisterUserDTO(
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User",
            role=UserRole.COMPETITOR,
        )

        result = await use_case.execute(dto)

        assert result.email == "test@example.com"
        assert result.full_name == "Test User"
        assert result.role == UserRole.COMPETITOR
        mock_user_repository.email_exists.assert_called_once_with("test@example.com")
        mock_password_service.hash_password.assert_called_once_with("SecurePass123!")
        mock_user_repository.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_exists(
        self,
        use_case,
        mock_user_repository,
    ):
        """Test registration fails when email exists."""
        mock_user_repository.email_exists.return_value = True

        dto = RegisterUserDTO(
            email="existing@example.com",
            password="SecurePass123!",
            full_name="Test User",
        )

        with pytest.raises(UserAlreadyExistsException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_register_user_weak_password(
        self,
        use_case,
    ):
        """Test registration fails with weak password."""
        dto = RegisterUserDTO(
            email="test@example.com",
            password="weak",
            full_name="Test User",
        )

        with pytest.raises(InvalidValueException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_register_user_invalid_email(
        self,
        use_case,
    ):
        """Test registration fails with invalid email."""
        dto = RegisterUserDTO(
            email="invalid-email",
            password="SecurePass123!",
            full_name="Test User",
        )

        with pytest.raises(InvalidValueException):
            await use_case.execute(dto)
