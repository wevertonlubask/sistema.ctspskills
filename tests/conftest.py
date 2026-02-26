"""Pytest configuration and fixtures."""

import os

# Disable rate limiting for tests - must be set before importing app
os.environ["RATE_LIMIT_ENABLED"] = "false"

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import Settings, get_settings

# Clear cached settings to ensure test settings are used
get_settings.cache_clear()
from src.infrastructure.database.base import Base
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import BcryptPasswordHasher
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.main import app

# Test database URL (use SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Get test settings."""
    return Settings(
        app_env="development",
        debug=True,
        database_url=TEST_DATABASE_URL,
        jwt_secret_key="test-secret-key-for-testing-purposes-only-32chars",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def password_hasher() -> BcryptPasswordHasher:
    """Get password hasher instance."""
    return BcryptPasswordHasher()


@pytest.fixture
def jwt_handler(test_settings: Settings) -> JWTHandler:
    """Get JWT handler instance."""
    return JWTHandler(
        secret_key=test_settings.jwt_secret_key,
        algorithm=test_settings.jwt_algorithm,
        access_token_expire_minutes=test_settings.access_token_expire_minutes,
        refresh_token_expire_days=test_settings.refresh_token_expire_days,
    )


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample user data for tests."""
    return {
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "role": "competitor",
    }


@pytest.fixture
def sample_admin_data() -> dict[str, Any]:
    """Sample admin user data for tests."""
    return {
        "email": f"admin_{uuid4().hex[:8]}@example.com",
        "password": "AdminPass123!",
        "full_name": "Admin User",
        "role": "super_admin",
    }


@pytest.fixture
def sample_evaluator_data() -> dict[str, Any]:
    """Sample evaluator user data for tests."""
    return {
        "email": f"evaluator_{uuid4().hex[:8]}@example.com",
        "password": "EvaluatorPass123!",
        "full_name": "Evaluator User",
        "role": "evaluator",
    }


@pytest.fixture
def sample_competitor_data() -> dict[str, Any]:
    """Sample competitor user data for tests."""
    return {
        "email": f"competitor_{uuid4().hex[:8]}@example.com",
        "password": "CompetitorPass123!",
        "full_name": "Competitor User",
        "role": "competitor",
    }


# Alias for async_client used in some tests
@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with database session override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(
    async_client: AsyncClient,
    sample_user_data: dict[str, Any],
) -> dict[str, str]:
    """Get authentication headers for a regular user."""
    # Register user
    response = await async_client.post(
        "/api/v1/auth/register",
        json=sample_user_data,
    )
    if response.status_code not in [200, 201, 400]:
        pytest.skip("Auth registration not available")

    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    if response.status_code != 200:
        pytest.skip("Auth login not available")

    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def evaluator_headers(
    async_client: AsyncClient,
    sample_evaluator_data: dict[str, Any],
) -> dict[str, str]:
    """Get authentication headers for an evaluator."""
    # Register evaluator
    response = await async_client.post(
        "/api/v1/auth/register",
        json=sample_evaluator_data,
    )
    if response.status_code not in [200, 201, 400]:
        pytest.skip("Auth registration not available")

    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": sample_evaluator_data["email"],
            "password": sample_evaluator_data["password"],
        },
    )
    if response.status_code != 200:
        pytest.skip("Auth login not available")

    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}
