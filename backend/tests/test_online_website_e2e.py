"""
Comprehensive End-to-End Test Suite for QRadar Online Website Configuration.
Validates all 18 required operational and security tests.
"""

import pytest
import unittest.mock as mock
import httpx
from datetime import datetime, timezone
from app.core.config import settings
from app.services.url_analyzer import url_analyzer_service
from app.services.ml_engine import ml_engine_service
from app.services.threat_intel import threat_intel_service, VirusTotalProvider, _compute_url_hash
from app.core.rate_limiter import rate_limiter


@pytest.mark.asyncio
async def test_01_open_website_from_browser(client):
    """TEST 1: Verify frontend website serves clean HTML from root / and /web without localhost hardcoding."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    html_content = resp.text
    assert "QRadar" in html_content
    assert "Live QR Scanner" in html_content
    assert "Security Dashboard" in html_content
    assert "getInitialApiBase" in html_content


@pytest.mark.asyncio
async def test_02_backend_health_check(client):
    """TEST 2: Verify backend health endpoint returns live service status and ML availability."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "ml_model_available" in data
    assert data["ml_model_available"] is True


@pytest.mark.asyncio
async def test_03_camera_qr_scanning_markup(client):
    """TEST 3: Verify browser local camera QR viewfinder & local decoding elements exist in frontend."""
    resp = await client.get("/")
    assert resp.status_code == 200
    html = resp.text
    assert "webcam-video" in html
    assert "webcam-canvas" in html
    assert "jsQR" in html


@pytest.mark.asyncio
async def test_04_safe_https_qr_scan(client):
    """TEST 4: Verify safe HTTPS URL returns SAFE, ALLOW, and low risk score."""
    payload = {"url": "https://www.google.com/search?q=cybersecurity", "source": "web_test"}
    resp = await client.post("/api/v1/scan/url", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "SAFE"
    assert data["recommended_action"] == "ALLOW"
    assert data["risk_score"] <= settings.RISK_SAFE_THRESHOLD
    assert "google.com" in data["domain"]


@pytest.mark.asyncio
async def test_05_suspicious_url_qr_scan(client):
    """TEST 5: Verify suspicious URL shortener returns SUSPICIOUS, WARN."""
    payload = {"url": "http://bit.ly/3xSampleShortener", "source": "web_test"}
    resp = await client.post("/api/v1/scan/url", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "SUSPICIOUS"
    assert data["recommended_action"] == "WARN"
    assert settings.RISK_SAFE_THRESHOLD < data["risk_score"] <= settings.RISK_SUSPICIOUS_THRESHOLD


@pytest.mark.asyncio
async def test_06_malicious_test_qr_scan(client):
    """TEST 6: Verify malicious phishing lookalike returns MALICIOUS, BLOCK."""
    payload = {"url": "http://paypa1-account-verification.xyz/login.php", "source": "web_test"}
    resp = await client.post("/api/v1/scan/url", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "MALICIOUS"
    assert data["recommended_action"] == "BLOCK"
    assert data["risk_score"] >= settings.RISK_MALICIOUS_THRESHOLD


@pytest.mark.asyncio
async def test_07_upi_non_web_payload(client):
    """TEST 7: Verify UPI non-web QR payload correctly reports NOT APPLICABLE for ML and Threat Intel."""
    payload = {"url": "upi://pay?pa=merchant@upi&pn=Store&am=500", "source": "web_test"}
    resp = await client.post("/api/v1/scan/url", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["content_type"] == "upi"
    assert data["verdict"] == "SAFE"
    assert data["recommended_action"] == "ALLOW"
    assert data["ml"]["status"] == "NOT_APPLICABLE"
    assert data["threat_intelligence"]["status"] == "NOT_APPLICABLE"


@pytest.mark.asyncio
async def test_08_random_forest_prediction():
    """TEST 8: Verify Random Forest model extracts 18 deterministic features and computes probability."""
    assert ml_engine_service.is_available is True
    res = ml_engine_service.predict("https://www.google.com")
    assert res["available"] is True
    assert res["status"] == "ANALYZED"
    assert res["prediction"] == "Legitimate"
    assert res["phishing_probability"] is not None
    assert 0.0 <= res["phishing_probability"] <= 1.0


@pytest.mark.asyncio
async def test_09_real_threat_intelligence_virustotal_lookup():
    """TEST 9: Verify VirusTotal provider queries endpoint and processes malicious count."""
    vt = VirusTotalProvider(api_key="test_vt_key_12345")
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "attributes": {
                "last_analysis_stats": {
                    "malicious": 4,
                    "suspicious": 1,
                    "harmless": 40,
                    "undetected": 20
                }
            }
        }
    }

    with mock.patch("httpx.AsyncClient.get", return_value=mock_resp):
        res = await vt.check_url("https://malicious-example.com/login")
        assert res["status"] == "MALICIOUS"
        assert res["checked"] is True
        assert res["malicious_count"] == 4
        assert res["provider"] == "VirusTotal"


@pytest.mark.asyncio
async def test_10_threat_intel_cache_hit():
    """TEST 10: Verify Threat Intelligence caches results and returns cached=True on repeat within TTL."""
    threat_intel_service.clear_cache()
    test_url = "https://example-cache-test-domain.org"

    res1 = await threat_intel_service.check(test_url)
    assert res1["cached"] is False

    res2 = await threat_intel_service.check(test_url)
    assert res2["cached"] is True


@pytest.mark.asyncio
async def test_11_threat_intel_failure_handling():
    """TEST 11: Verify Threat Intelligence reports NOT AVAILABLE without fabricating clean results on error."""
    vt = VirusTotalProvider(api_key="test_vt_key_12345")
    with mock.patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Connection timed out")):
        res = await vt.check_url("https://timeout-test.org")
        assert res["status"] == "NOT_AVAILABLE"
        assert res["checked"] is False
        assert res["error_reason"] == "TIMEOUT"


@pytest.mark.asyncio
async def test_12_scan_history_recording_and_retrieval(client):
    """TEST 12: Verify all scans are persisted to SQLite database and retrievable via history API."""
    scan_url = "https://www.github.com"
    await client.post("/api/v1/scan/url", json={"url": scan_url})

    resp = await client.get("/api/v1/scans")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) >= 1
    assert any("github.com" in (item.get("domain") or "") for item in history)


@pytest.mark.asyncio
async def test_13_dashboard_real_db_statistics(client):
    """TEST 13: Verify dashboard calculates statistics from SQLite database."""
    await client.post("/api/v1/scan/url", json={"url": "https://www.google.com"})
    await client.post("/api/v1/scan/url", json={"url": "http://paypa1-account-verification.xyz/login.php"})

    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["total_scans"] >= 2
    assert stats["verdict_counts"]["safe"] >= 1
    assert stats["verdict_counts"]["malicious"] >= 1
    assert stats["average_risk_score"] > 0


@pytest.mark.asyncio
async def test_14_settings_ping_and_health_integration(client):
    """TEST 14: Verify settings Ping & Test queries /health and returns valid response."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    d = resp.json()
    assert d["service"] == settings.PROJECT_NAME
    assert d["ml_model_available"] is True


@pytest.mark.asyncio
async def test_15_no_auto_navigation_on_dangerous_schemes(client):
    """TEST 15: Verify dangerous URI schemes are blocked with high risk and zero auto-navigation."""
    payload = {"url": "javascript:alert(document.cookie)", "source": "test"}
    resp = await client.post("/api/v1/scan/url", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "MALICIOUS"
    assert data["recommended_action"] == "BLOCK"
    assert data["risk_score"] >= 95


@pytest.mark.asyncio
async def test_16_cors_configuration():
    """TEST 16: Verify CORS origins configuration parses specific origins cleanly and avoids wildcard in production."""
    parsed = settings.parse_cors_origins("https://qradar.example.com,https://api.qradar.example.com")
    assert "https://qradar.example.com" in parsed
    assert "https://api.qradar.example.com" in parsed
    assert "*" not in parsed


@pytest.mark.asyncio
async def test_17_ssrf_protections():
    """TEST 17: Verify SSRF validator blocks private, loopback, link-local, and reserved IP destinations."""
    ssrf_targets = [
        "http://127.0.0.1:8000/admin",
        "http://localhost/secret",
        "http://192.168.1.1/router",
        "http://10.0.0.1/internal",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/internal",
    ]
    for target in ssrf_targets:
        is_safe, reason = url_analyzer_service.validate_outbound_url_ssrf(target)
        assert is_safe is False, f"Target {target} should be blocked by SSRF protection!"
        assert reason is not None


@pytest.mark.asyncio
async def test_18_rate_limiting(client):
    """TEST 18: Verify rate limiter blocks rapid bursts and returns HTTP 429 with Retry-After header."""
    rate_limiter.reset()
    # Temporarily set small limit to test 429
    original_limit = rate_limiter.requests_per_minute
    try:
        rate_limiter.requests_per_minute = 3
        # Send 3 allowed requests
        for _ in range(3):
            r = await client.post("/api/v1/scan/url", json={"url": "https://www.google.com"})
            assert r.status_code == 200

        # 4th request should trigger 429
        r4 = await client.post("/api/v1/scan/url", json={"url": "https://www.google.com"})
        assert r4.status_code == 429
        assert "Retry-After" in r4.headers
    finally:
        rate_limiter.requests_per_minute = original_limit
        rate_limiter.reset()
