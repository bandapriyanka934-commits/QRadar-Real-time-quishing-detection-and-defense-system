"""
Process-Local In-Memory Sliding Window Rate Limiter for QRadar API Endpoints.
Guards /api/v1/scan/* endpoints against rapid flooding.
Returns HTTP 429 Too Many Requests with Retry-After header when threshold exceeded.
"""

import time
import logging
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status
from app.core.config import settings

logger = logging.getLogger("qradar.rate_limiter")


class InMemoryRateLimiter:
    """
    Sliding-window request rate limiter keyed by client host IP.
    Process-local (not distributed), tailored for local development and demos.
    """

    def __init__(self, requests_per_minute: int = 60, enabled: bool = True):
        self.requests_per_minute = requests_per_minute
        self.enabled = enabled
        self._history: Dict[str, List[float]] = {}

    def is_rate_limited(self, client_ip: str) -> Tuple[bool, int]:
        """
        Evaluates whether client has exceeded allowed requests per minute.
        Returns (is_limited, retry_after_seconds).
        """
        if not self.enabled:
            return False, 0

        now = time.time()
        window_start = now - 60.0

        # Clean timestamps older than 1 minute
        history = [ts for ts in self._history.get(client_ip, []) if ts > window_start]
        self._history[client_ip] = history

        if len(history) >= self.requests_per_minute:
            oldest = history[0]
            retry_after = max(1, int(oldest + 60.0 - now))
            return True, retry_after

        # Record this request
        history.append(now)
        self._history[client_ip] = history
        return False, 0

    def reset(self):
        """Clears all tracking history (useful for test isolation)."""
        self._history.clear()


# Global singleton rate limiter instance
rate_limiter = InMemoryRateLimiter(
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    enabled=settings.RATE_LIMIT_ENABLED
)


async def rate_limit_dependency(request: Request):
    """
    FastAPI dependency that enforces rate limiting on route handlers.
    Raises HTTPException(status_code=429) with Retry-After header if limit exceeded.
    """
    if not settings.RATE_LIMIT_ENABLED:
        return

    # Extract client IP from headers or client host
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "127.0.0.1")
    )

    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip)
    if is_limited:
        logger.warning(f"[RATE LIMIT] Client '{client_ip}' exceeded limit of {settings.RATE_LIMIT_PER_MINUTE} req/min.")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {settings.RATE_LIMIT_PER_MINUTE} scans allowed per minute.",
            headers={"Retry-After": str(retry_after)}
        )
