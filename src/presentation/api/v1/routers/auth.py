"""Authentication router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.identity.dtos.auth_dto import (
    ChangePasswordDTO,
    LoginDTO,
    LogoutDTO,
    RefreshTokenDTO,
    RegisterUserDTO,
)
from src.application.identity.use_cases.change_password import ChangePasswordUseCase
from src.application.identity.use_cases.login_user import LoginUserUseCase
from src.application.identity.use_cases.logout_user import LogoutUserUseCase
from src.application.identity.use_cases.refresh_token import RefreshTokenUseCase
from src.application.identity.use_cases.register_user import RegisterUserUseCase
from src.domain.identity.entities.user import User
from src.infrastructure.container import get_container
from src.infrastructure.database.repositories.refresh_token_repository_impl import (
    SQLAlchemyRefreshTokenRepository,
)
from src.infrastructure.database.repositories.user_repository_impl import (
    SQLAlchemyUserRepository,
)
from src.presentation.api.v1.dependencies.auth import get_current_active_user
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.auth_schema import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from src.presentation.schemas.common import MessageResponse
from src.presentation.schemas.user_schema import UserResponse

router = APIRouter()


def get_client_info(request: Request) -> tuple[str | None, str | None]:
    """Extract client information from request."""
    user_agent = request.headers.get("user-agent")
    # Get real IP considering proxies
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else None
    return user_agent, ip_address


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account with email and password.",
)
async def register(
    data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Register a new user."""
    container = get_container()

    use_case = RegisterUserUseCase(
        user_repository=SQLAlchemyUserRepository(db),
        password_service=container.password_service,
    )

    dto = RegisterUserDTO(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        role=data.role,
        must_change_password=data.must_change_password,
    )

    user_dto = await use_case.execute(dto)
    await db.commit()

    return UserResponse(
        id=user_dto.id,
        email=user_dto.email,
        full_name=user_dto.full_name,
        role=user_dto.role,
        status=user_dto.status,
        created_at=user_dto.created_at,
        updated_at=user_dto.updated_at,
        last_login_at=user_dto.last_login_at,
        must_change_password=user_dto.must_change_password,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate user and return access and refresh tokens.",
)
async def login(
    data: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    """Authenticate user and return tokens."""
    container = get_container()
    user_agent, ip_address = get_client_info(request)

    use_case = LoginUserUseCase(
        user_repository=SQLAlchemyUserRepository(db),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(db),
        password_service=container.password_service,
        jwt_handler=container.jwt_handler,
    )

    dto = LoginDTO(email=data.email, password=data.password)
    result = await use_case.execute(dto, user_agent=user_agent, ip_address=ip_address)
    await db.commit()

    return LoginResponse(
        access_token=result.tokens.access_token,
        refresh_token=result.tokens.refresh_token,
        token_type=result.tokens.token_type,
        expires_at=result.tokens.expires_at,
        user=UserResponse(
            id=result.user.id,
            email=result.user.email,
            full_name=result.user.full_name,
            role=result.user.role,
            status=result.user.status,
            created_at=result.user.created_at,
            updated_at=result.user.updated_at,
            last_login_at=result.user.last_login_at,
            must_change_password=result.user.must_change_password,
        ),
    )


@router.post(
    "/login/form",
    response_model=LoginResponse,
    summary="User login (OAuth2 form)",
    description="Authenticate user using OAuth2 password flow.",
    include_in_schema=True,
)
async def login_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    """Authenticate user using OAuth2 password form."""
    container = get_container()
    user_agent, ip_address = get_client_info(request)

    use_case = LoginUserUseCase(
        user_repository=SQLAlchemyUserRepository(db),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(db),
        password_service=container.password_service,
        jwt_handler=container.jwt_handler,
    )

    dto = LoginDTO(email=form_data.username, password=form_data.password)
    result = await use_case.execute(dto, user_agent=user_agent, ip_address=ip_address)
    await db.commit()

    return LoginResponse(
        access_token=result.tokens.access_token,
        refresh_token=result.tokens.refresh_token,
        token_type=result.tokens.token_type,
        expires_at=result.tokens.expires_at,
        user=UserResponse(
            id=result.user.id,
            email=result.user.email,
            full_name=result.user.full_name,
            role=result.user.role,
            status=result.user.status,
            created_at=result.user.created_at,
            updated_at=result.user.updated_at,
            last_login_at=result.user.last_login_at,
            must_change_password=result.user.must_change_password,
        ),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh tokens",
    description="Get new access token using refresh token.",
)
async def refresh_token(
    data: RefreshTokenRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Refresh access token."""
    container = get_container()
    user_agent, ip_address = get_client_info(request)

    use_case = RefreshTokenUseCase(
        user_repository=SQLAlchemyUserRepository(db),
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(db),
        jwt_handler=container.jwt_handler,
    )

    dto = RefreshTokenDTO(refresh_token=data.refresh_token)
    result = await use_case.execute(dto, user_agent=user_agent, ip_address=ip_address)
    await db.commit()

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        expires_at=result.expires_at,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User logout",
    description="Invalidate refresh token to logout user.",
)
async def logout(
    data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Logout user by revoking refresh token."""
    use_case = LogoutUserUseCase(
        refresh_token_repository=SQLAlchemyRefreshTokenRepository(db),
    )

    dto = LogoutDTO(refresh_token=data.refresh_token)
    await use_case.execute(dto)
    await db.commit()

    return MessageResponse(message="Successfully logged out")


@router.post(
    "/change-password",
    response_model=UserResponse,
    summary="Change password",
    description="Change current user's password. Clears the must_change_password flag.",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Change user password."""
    container = get_container()

    use_case = ChangePasswordUseCase(
        user_repository=SQLAlchemyUserRepository(db),
        password_service=container.password_service,
    )

    dto = ChangePasswordDTO(
        current_password=data.current_password,
        new_password=data.new_password,
    )

    user_dto = await use_case.execute(current_user.id, dto)
    await db.commit()

    return UserResponse(
        id=user_dto.id,
        email=user_dto.email,
        full_name=user_dto.full_name,
        role=user_dto.role,
        status=user_dto.status,
        created_at=user_dto.created_at,
        updated_at=user_dto.updated_at,
        last_login_at=user_dto.last_login_at,
        must_change_password=user_dto.must_change_password,
    )
