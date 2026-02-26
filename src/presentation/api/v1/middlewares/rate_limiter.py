"""Rate limiting middleware (RN15)."""

import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.settings import get_settings


@dataclass
class RateLimitEntry:
    """Rate limit entry for a client."""

    requests: list[float] = field(default_factory=list)


class RateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(
        self,
        requests_limit: int = 100,
        window_seconds: int = 60,
    ) -> None:
        """Initialize rate limiter.

        Args:
            requests_limit: Maximum requests allowed per window.
            window_seconds: Time window in seconds.
        """
        self._requests_limit = requests_limit
        self._window_seconds = window_seconds
        self._clients: dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)

    def _get_client_key(self, request: Request) -> str:
        """Get unique client identifier.

        Uses X-Forwarded-For header if behind proxy, otherwise client host.
        For authenticated requests, uses user ID if available.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return client_ip  # type: ignore[no-any-return]

    def _cleanup_old_requests(self, entry: RateLimitEntry, now: float) -> None:
        """Remove expired requests from the sliding window."""
        cutoff = now - self._window_seconds
        entry.requests = [ts for ts in entry.requests if ts > cutoff]

    def is_allowed(self, request: Request) -> tuple[bool, dict]:
        """Check if request is allowed.

        Args:
            request: FastAPI request object.

        Returns:
            Tuple of (is_allowed, rate_limit_info).
        """
        now = time.time()
        client_key = self._get_client_key(request)
        entry = self._clients[client_key]

        self._cleanup_old_requests(entry, now)

        remaining = max(0, self._requests_limit - len(entry.requests))
        reset_time = int(now + self._window_seconds)

        info = {
            "X-RateLimit-Limit": str(self._requests_limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }

        if len(entry.requests) >= self._requests_limit:
            retry_after = int(entry.requests[0] + self._window_seconds - now) + 1
            info["Retry-After"] = str(max(1, retry_after))
            return False, info

        entry.requests.append(now)
        info["X-RateLimit-Remaining"] = str(remaining - 1)
        return True, info


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    # Paths that should be excluded from rate limiting
    EXCLUDED_PATHS = {
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    def __init__(
        self,
        app: Callable,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        """Initialize middleware.

        Args:
            app: FastAPI application.
            rate_limiter: Optional rate limiter instance.
        """
        super().__init__(app)
        if rate_limiter is None:
            settings = get_settings()
            rate_limiter = RateLimiter(
                requests_limit=settings.rate_limit_requests,
                window_seconds=settings.rate_limit_period_seconds,
            )
        self._rate_limiter = rate_limiter

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request with rate limiting.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response with rate limit headers.
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        is_allowed, rate_info = self._rate_limiter.is_allowed(request)

        if not is_allowed:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": rate_info.get("Retry-After"),
                },
            )
            for header, value in rate_info.items():
                response.headers[header] = value
            return response

        response = await call_next(request)

        # Add rate limit headers to response
        for header, value in rate_info.items():
            if header != "Retry-After":
                response.headers[header] = value

        return response


def create_rate_limiter() -> RateLimiter:
    """Create rate limiter instance from settings."""
    settings = get_settings()
    return RateLimiter(
        requests_limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_period_seconds,
    )
