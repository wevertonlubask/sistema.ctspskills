"""Tests for rate limiter middleware."""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.presentation.api.v1.middlewares.rate_limiter import (
    RateLimiter,
    RateLimitMiddleware,
)


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_allows_requests_within_limit(self) -> None:
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(requests_limit=10, window_seconds=60)
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = None

        for _ in range(10):
            is_allowed, info = limiter.is_allowed(request)
            assert is_allowed is True
            assert "X-RateLimit-Limit" in info
            assert info["X-RateLimit-Limit"] == "10"

    def test_blocks_requests_over_limit(self) -> None:
        """Test that requests over limit are blocked."""
        limiter = RateLimiter(requests_limit=5, window_seconds=60)
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = None

        # Make 5 allowed requests
        for _ in range(5):
            is_allowed, _ = limiter.is_allowed(request)
            assert is_allowed is True

        # 6th request should be blocked
        is_allowed, info = limiter.is_allowed(request)
        assert is_allowed is False
        assert "Retry-After" in info

    def test_different_clients_have_separate_limits(self) -> None:
        """Test that different clients have separate rate limits."""
        limiter = RateLimiter(requests_limit=2, window_seconds=60)

        request1 = MagicMock(spec=Request)
        request1.client.host = "192.168.1.1"
        request1.headers.get.return_value = None

        request2 = MagicMock(spec=Request)
        request2.client.host = "192.168.1.2"
        request2.headers.get.return_value = None

        # Make 2 requests from client 1
        for _ in range(2):
            is_allowed, _ = limiter.is_allowed(request1)
            assert is_allowed is True

        # Client 1 should be blocked
        is_allowed, _ = limiter.is_allowed(request1)
        assert is_allowed is False

        # Client 2 should still be allowed
        is_allowed, _ = limiter.is_allowed(request2)
        assert is_allowed is True

    def test_uses_forwarded_for_header(self) -> None:
        """Test that X-Forwarded-For header is used for client identification."""
        limiter = RateLimiter(requests_limit=2, window_seconds=60)

        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "10.0.0.1, 10.0.0.2"

        # First request
        is_allowed, _ = limiter.is_allowed(request)
        assert is_allowed is True

        # Change the forwarded header
        request2 = MagicMock(spec=Request)
        request2.client.host = "192.168.1.1"
        request2.headers.get.return_value = "10.0.0.3"

        # Should be a different client
        is_allowed, _ = limiter.is_allowed(request2)
        assert is_allowed is True

    def test_remaining_count_decreases(self) -> None:
        """Test that remaining count decreases with each request."""
        limiter = RateLimiter(requests_limit=5, window_seconds=60)
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = None

        _, info = limiter.is_allowed(request)
        assert info["X-RateLimit-Remaining"] == "4"

        _, info = limiter.is_allowed(request)
        assert info["X-RateLimit-Remaining"] == "3"

        _, info = limiter.is_allowed(request)
        assert info["X-RateLimit-Remaining"] == "2"


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware."""

    @pytest.fixture
    def app_with_rate_limit(self) -> FastAPI:
        """Create a FastAPI app with rate limiting."""
        app = FastAPI()
        limiter = RateLimiter(requests_limit=5, window_seconds=60)
        app.add_middleware(RateLimitMiddleware, rate_limiter=limiter)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "ok"}

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        return app

    def test_adds_rate_limit_headers(self, app_with_rate_limit: FastAPI) -> None:
        """Test that rate limit headers are added to responses."""
        client = TestClient(app_with_rate_limit)
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_returns_429_when_exceeded(self, app_with_rate_limit: FastAPI) -> None:
        """Test that 429 is returned when rate limit is exceeded."""
        client = TestClient(app_with_rate_limit)

        # Make 5 allowed requests
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

        # 6th request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert "rate limit exceeded" in response.json()["detail"].lower()

    def test_excludes_health_endpoint(self, app_with_rate_limit: FastAPI) -> None:
        """Test that health endpoint is excluded from rate limiting."""
        client = TestClient(app_with_rate_limit)

        # Make many requests to health - should all succeed
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
            # Health endpoint should not have rate limit headers
            assert "X-RateLimit-Limit" not in response.headers
