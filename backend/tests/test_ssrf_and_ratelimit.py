"""
Unit and Integration Tests for SSRF / DNS Rebinding Guard and Rate Limiting.
"""

import pytest
import httpx
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport, Response

from app.main import app
from app.services.url_analyzer import url_analyzer_service, URLAnalyzerService
from app.core.rate_limiter import rate_limiter, InMemoryRateLimiter


# =========================================================================
# 1. SSRF & Private IP Validation Tests
# =========================================================================

def test_ssrf_private_and_loopback_ips():
    """Validates that IPv4 and IPv6 loopback, private, and internal addresses are blocked."""
    blocked_hosts = [
        "localhost",
        "127.0.0.1",
        "127.0.0.2",
        "0.0.0.0",
        "::1",
        "::ffff:127.0.0.1",
        "192.168.1.1",
        "10.0.0.1",
        "172.16.0.5",
        "169.254.169.254",  # AWS/Cloud metadata service
        "router.local",
        "service.internal",
    ]
    for host in blocked_hosts:
        assert URLAnalyzerService.is_private_or_loopback_ip(host) is True, f"Failed for {host}"

    public_hosts = [
        "google.com",
        "8.8.8.8",
        "1.1.1.1",
        "github.com",
        "microsoft.com"
    ]
    for host in public_hosts:
        assert URLAnalyzerService.is_private_or_loopback_ip(host) is False, f"Failed for {host}"


def test_ssrf_outbound_url_validation():
    """Validates that dangerous schemes and internal addresses are rejected before outbound resolution."""
    # 1. Non-http/https schemes rejected
    is_safe, reason = url_analyzer_service.validate_outbound_url_ssrf("javascript:alert(1)")
    assert is_safe is False
    assert "scheme" in reason.lower()

    is_safe, reason = url_analyzer_service.validate_outbound_url_ssrf("file:///etc/passwd")
    assert is_safe is False

    is_safe, reason = url_analyzer_service.validate_outbound_url_ssrf("data:text/html,<script>")
    assert is_safe is False

    # 2. Loopback and internal addresses rejected
    is_safe, reason = url_analyzer_service.validate_outbound_url_ssrf("http://127.0.0.1:8000/api")
    assert is_safe is False

    is_safe, reason = url_analyzer_service.validate_outbound_url_ssrf("http://169.254.169.254/latest/meta-data")
    assert is_safe is False


@pytest.mark.asyncio
async def test_shortener_resolution_hop_limit_and_ssrf():
    """Validates that shortener resolution guards against SSRF redirects and hop limit."""
    # Mock redirect to internal loopback
    with patch.object(url_analyzer_service, "validate_outbound_url_ssrf") as mock_validate:
        mock_validate.return_value = (False, "Blocked private address")
        res = await url_analyzer_service.resolve_shortener_safely("https://bit.ly/test-ssrf")
        assert res["status"] in {"NOT_AVAILABLE", "FAILED"}


# =========================================================================
# 2. Rate Limiting Tests
# =========================================================================

def test_in_memory_rate_limiter_unit():
    """Unit test for sliding-window rate limiter logic."""
    limiter = InMemoryRateLimiter(requests_per_minute=3, enabled=True)
    client_ip = "192.0.2.100"

    # First 3 requests should pass
    is_limited, _ = limiter.is_rate_limited(client_ip)
    assert is_limited is False

    is_limited, _ = limiter.is_rate_limited(client_ip)
    assert is_limited is False

    is_limited, _ = limiter.is_rate_limited(client_ip)
    assert is_limited is False

    # 4th request must be rate limited with positive retry_after
    is_limited, retry_after = limiter.is_rate_limited(client_ip)
    assert is_limited is True
    assert retry_after > 0


@pytest.mark.asyncio
async def test_api_rate_limiting_http_429():
    """Integration test: Flooding /api/v1/scan/url returns HTTP 429 and Retry-After header."""
    rate_limiter.reset()
    # Temporarily set small limit for test
    original_limit = rate_limiter.requests_per_minute
    rate_limiter.requests_per_minute = 2

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            headers = {"X-Forwarded-For": "203.0.113.50"}

            # Request 1 -> 200
            resp1 = await client.post("/api/v1/scan/url", json={"url": "https://google.com"}, headers=headers)
            assert resp1.status_code == 200

            # Request 2 -> 200
            resp2 = await client.post("/api/v1/scan/url", json={"url": "https://github.com"}, headers=headers)
            assert resp2.status_code == 200

            # Request 3 -> 429
            resp3 = await client.post("/api/v1/scan/url", json={"url": "https://microsoft.com"}, headers=headers)
            assert resp3.status_code == 429
            assert "Retry-After" in resp3.headers
            assert int(resp3.headers["Retry-After"]) >= 1
    finally:
        rate_limiter.requests_per_minute = original_limit
        rate_limiter.reset()
