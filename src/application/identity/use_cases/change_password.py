"""Change password use case."""

from uuid import UUID

from src.application.identity.dtos.auth_dto import ChangePasswordDTO
from src.application.identity.dtos.user_dto import UserDTO
from src.domain.identity.exceptions import UserNotFoundException
from src.domain.identity.repositories.user_repository import UserRepository
from src.domain.identity.services.password_service import PasswordService
from src.domain.identity.value_objects.password import Password
from src.shared.exceptions import AuthenticationException, ErrorCode


class ChangePasswordUseCase:
    """Use case for changing user password."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service

    async def execute(self, user_id: UUID, dto: ChangePasswordDTO) -> UserDTO:
        """Change user password.

        Args:
            user_id: ID of the user changing password.
            dto: Password change data.

        Returns:
            Updated user DTO.

        Raises:
            UserNotFoundException: If user not found.
            AuthenticationException: If current password is wrong.
            InvalidValueException: If new password is invalid.
        """
        # Get user
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(identifier=str(user_id), field="id")

        # Verify current password
        if not self._password_service.verify_password(
            dto.current_password, user.password.hashed_value
        ):
            raise AuthenticationException(
                message="Current password is incorrect",
                code=ErrorCode.INVALID_CREDENTIALS,
            )

        # Validate new password strength
        Password.validate_raw(dto.new_password)

        # Hash new password
        hashed_password = self._password_service.hash_password(dto.new_password)
        new_password = Password(hashed_password)

        # Update password (this also clears must_change_password flag)
        user.update_password(new_password)

        # Persist changes
        updated_user = await self._user_repository.update(user)

        return UserDTO.from_entity(updated_user)
