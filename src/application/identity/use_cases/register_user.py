"""Register user use case."""

from src.application.identity.dtos.auth_dto import RegisterUserDTO
from src.application.identity.dtos.user_dto import UserDTO
from src.domain.identity.entities.user import User
from src.domain.identity.exceptions import UserAlreadyExistsException
from src.domain.identity.repositories.user_repository import UserRepository
from src.domain.identity.services.password_service import PasswordService
from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.password import Password


class RegisterUserUseCase:
    """Use case for registering a new user."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service

    async def execute(self, dto: RegisterUserDTO) -> UserDTO:
        """Register a new user.

        Args:
            dto: Registration data.

        Returns:
            Created user DTO.

        Raises:
            UserAlreadyExistsException: If email is already registered.
            InvalidValueException: If email or password is invalid.
        """
        # Check if email already exists
        if await self._user_repository.email_exists(dto.email):
            raise UserAlreadyExistsException(email=dto.email)

        # Validate password strength
        Password.validate_raw(dto.password)

        # Create email value object (validates format)
        email = Email(dto.email)

        # Hash password
        hashed_password = self._password_service.hash_password(dto.password)
        password = Password(hashed_password)

        # Create user entity
        user = User(
            email=email,
            password=password,
            full_name=dto.full_name.strip(),
            role=dto.role,
            must_change_password=dto.must_change_password,
        )

        # Persist user
        created_user = await self._user_repository.add(user)

        return UserDTO.from_entity(created_user)
