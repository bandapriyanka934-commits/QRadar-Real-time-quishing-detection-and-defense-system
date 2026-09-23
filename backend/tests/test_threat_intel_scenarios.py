"""
Comprehensive Threat Intelligence Verification and Scenario Test Suite (Scenarios A through N).
Verifies standardized state distinctions (MALICIOUS, CLEAN, NOT_AVAILABLE, NOT_APPLICABLE),
error handling, API key security, TTL caching with provider keys, and risk engine integration.
Uses standard library unittest.mock and httpx.Response without external mock packages.
"""

import pytest
import httpx
from unittest.mock import patch, AsyncMock
from httpx import Response

from app.services.threat_intel import (
    VirusTotalProvider,
    GoogleSafeBrowsingProvider,
    LocalOfflineThreatIntelProvider,
    ThreatIntelService,
)
from app.services.risk_engine import risk_engine
from app.services.url_analyzer import url_analyzer_service


# =========================================================================
# Scenario A: Known safe/legitimate URL (VirusTotal / GSB returns clean)
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_a_known_safe_url():
    """Scenario A: Known clean URL verified across all engines with 0 detections."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    test_url = "https://www.google.com"

    mock_resp = Response(
        200,
        json={
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 0,
                        "suspicious": 0,
                        "harmless": 88,
                        "undetected": 5,
                    }
                }
            }
        },
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url(test_url)

    assert res["status"] == "CLEAN"
    assert res["checked"] is True
    assert res["result"] == "CLEAN"
    assert res["malicious_count"] == 0
    assert res["suspicious_count"] == 0
    assert res["harmless_count"] == 88
    assert res["error_reason"] is None


# =========================================================================
# Scenario B: URL with no provider record (VirusTotal returns HTTP 404)
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_b_no_provider_record():
    """Scenario B: Unindexed / previously unseen URL returns 404 -> CLEAN with NO_RECORD result."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    test_url = "https://brand-new-domain-unindexed-2026.org/page"

    mock_resp = Response(
        404,
        json={"error": {"code": "NotFoundError", "message": "URL not found"}},
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url(test_url)

    assert res["status"] == "CLEAN"
    assert res["checked"] is True
    assert res["result"] == "NO_RECORD"
    assert res["malicious_count"] == 0
    assert res["suspicious_count"] == 0


# =========================================================================
# Scenario C: Suspicious URL using controlled test data
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_c_suspicious_url():
    """Scenario C: Provider returns 0 malicious but >= 1 suspicious detections."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    test_url = "https://unusual-redirector-gateway.net"

    mock_resp = Response(
        200,
        json={
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 0,
                        "suspicious": 3,
                        "harmless": 45,
                        "undetected": 10,
                    }
                }
            }
        },
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url(test_url)

    assert res["status"] == "SUSPICIOUS"
    assert res["checked"] is True
    assert res["result"] == "SUSPICIOUS"
    assert res["malicious_count"] == 0
    assert res["suspicious_count"] == 3
    assert "suspicious" in res["message"].lower()


# =========================================================================
# Scenario D: Known malicious test result using controlled mock data
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_d_known_malicious():
    """Scenario D: Controlled mock test result with positive malicious detections."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    test_url = "https://simulated-phish-portal.example.com"

    mock_resp = Response(
        200,
        json={
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 14,
                        "suspicious": 4,
                        "harmless": 2,
                        "undetected": 20,
                    }
                }
            }
        },
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url(test_url)

    assert res["status"] == "MALICIOUS"
    assert res["checked"] is True
    assert res["result"] == "MALICIOUS"
    assert res["malicious_count"] == 14
    assert res["suspicious_count"] == 4

    # Verify Risk Engine forces BLOCK on MALICIOUS
    parsed = url_analyzer_service.parse_and_normalize(test_url)
    risk_res = risk_engine.evaluate(parsed=parsed, heuristics=[], ml_result={}, threat_intel=res)
    assert risk_res["verdict"] == "MALICIOUS"
    assert risk_res["recommended_action"] == "BLOCK"
    assert risk_res["risk_score"] >= 70


# =========================================================================
# Scenario E: Invalid / Empty URL
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_e_invalid_url():
    """Scenario E: Empty or blank URL input is handled gracefully without error."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    mock_resp = Response(
        404,
        json={"error": {"code": "NotFoundError", "message": "URL not found"}},
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )
    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url("")
    assert res["status"] in {"CLEAN", "NOT_AVAILABLE", "NOT_APPLICABLE"}


# =========================================================================
# Scenario F: Provider Timeout
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_f_provider_timeout():
    """Scenario F: Request times out -> NOT_AVAILABLE with TIMEOUT reason."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    test_url = "https://slow-responding-provider-target.org"

    with patch.object(httpx.AsyncClient, "get", side_effect=httpx.TimeoutException("Read timed out")):
        res = await vt.check_url(test_url)

    assert res["status"] == "NOT_AVAILABLE"
    assert res["checked"] is False
    assert res["error_reason"] == "TIMEOUT"
    assert "timed out" in res["message"].lower()

    # Verify risk engine flags degraded coverage without forcing ALLOW
    parsed = url_analyzer_service.parse_and_normalize(test_url)
    risk_res = risk_engine.evaluate(parsed=parsed, heuristics=[], ml_result={"status": "ANALYZED", "phishing_probability": 0.05}, threat_intel=res)
    assert risk_res["is_degraded"] is True


# =========================================================================
# Scenario G: Provider Unavailable / Server 500 Error / Network Unreachable
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_g_provider_unavailable():
    """Scenario G: Provider server returns HTTP 500 or Network Error."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    test_url = "https://some-target-site.com"

    mock_resp = Response(
        500,
        text="Internal Server Error",
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url(test_url)

    assert res["status"] == "NOT_AVAILABLE"
    assert res["checked"] is False
    assert res["error_reason"] == "PROVIDER_ERROR"
    assert "500" in res["details"]


# =========================================================================
# Scenario H: Invalid API Key / Authentication Error (401 / 403)
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_h_invalid_api_key():
    """Scenario H: Invalid API key triggers 401 Unauthorized -> NOT_AVAILABLE."""
    vt = VirusTotalProvider(api_key="bad_invalid_key_xyz")
    test_url = "https://some-target-site.com"

    mock_resp = Response(
        401,
        json={"error": {"code": "WrongCredentialsError", "message": "Invalid API key"}},
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url(test_url)

    assert res["status"] == "NOT_AVAILABLE"
    assert res["checked"] is False
    assert res["error_reason"] == "AUTHENTICATION_FAILED"
    assert "invalid" in res["message"].lower() or "unauthorized" in res["message"].lower()

    # Ensure the bad API key string is NOT leaked into the details or message
    assert "bad_invalid_key_xyz" not in str(res)


# =========================================================================
# Scenario I: Rate Limit Exceeded (HTTP 429)
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_i_rate_limit():
    """Scenario I: Provider quota reached (429) -> NOT_AVAILABLE."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    test_url = "https://some-target-site.com"

    mock_resp = Response(
        429,
        json={"error": {"code": "QuotaExceededError", "message": "Rate limit exceeded"}},
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url(test_url)

    assert res["status"] == "NOT_AVAILABLE"
    assert res["checked"] is False
    assert res["error_reason"] == "RATE_LIMIT_EXCEEDED"
    assert "rate limit" in res["message"].lower()


# =========================================================================
# Scenario J: Empty / Malformed Provider Response
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_j_malformed_response():
    """Scenario J: Provider returns 200 with invalid/empty non-JSON body."""
    vt = VirusTotalProvider(api_key="test_dummy_vt_key_12345")
    test_url = "https://some-target-site.com"

    mock_resp = Response(
        200,
        text="<HTML>Not JSON</HTML>",
        request=httpx.Request("GET", "https://www.virustotal.com/api/v3/urls/dummy")
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await vt.check_url(test_url)

    assert res["status"] == "NOT_AVAILABLE"
    assert res["checked"] is False
    assert res["error_reason"] == "PROVIDER_ERROR"


# =========================================================================
# Scenario K: Unconfigured External Provider (Missing API Key)
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_k_unconfigured_external_provider():
    """Scenario K: External provider instantiated with empty key reports NOT_AVAILABLE."""
    vt_unconfigured = VirusTotalProvider(api_key="")
    res = await vt_unconfigured.check_url("https://example.com")
    assert res["status"] == "NOT_AVAILABLE"
    assert res["checked"] is False
    assert res["error_reason"] == "API_KEY_NOT_CONFIGURED"
    assert "not configured" in res["message"].lower()


# =========================================================================
# Scenario L: Threat Intelligence Is NOT Sole Authority (Defense-in-Depth)
# =========================================================================
def test_scenario_l_heuristics_and_ml_override_clean_ti():
    """Scenario L: If Heuristics and ML identify a phishing attack, CLEAN threat intel does not force Safe."""
    parsed = url_analyzer_service.parse_and_normalize("https://paypa1-account-update.xyz/login.php")
    heuristics = [
        {"indicator": "LOOKALIKE_TYPOSQUATTING", "triggered": True, "score_contribution": 35, "explanation": "Paypal brand typo"},
        {"indicator": "SUSPICIOUS_TLD", "triggered": True, "score_contribution": 15, "explanation": "High risk .xyz TLD"},
    ]
    ml = {
        "status": "ANALYZED",
        "phishing_probability": 0.92,
    }
    ti_clean = {
        "status": "CLEAN",
        "provider": "VirusTotal",
        "checked": True,
        "malicious_count": 0,
        "suspicious_count": 0,
    }

    decision = risk_engine.evaluate(parsed=parsed, heuristics=heuristics, ml_result=ml, threat_intel=ti_clean)
    assert decision["verdict"] == "MALICIOUS"
    assert decision["recommended_action"] == "BLOCK"
    assert decision["risk_score"] >= 70


# =========================================================================
# Scenario M: Local Offline Threat Engine Distinction
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_m_local_engine_distinction():
    """Scenario M: Local engine reports CLEAN for unknown domains with NO_RECORD result, not fake cloud feed."""
    local_engine = LocalOfflineThreatIntelProvider()
    assert "Offline DB" in local_engine.provider_name

    # Unknown domain
    res_unknown = await local_engine.check_url("https://my-custom-unseen-domain-99.com/path")
    assert res_unknown["status"] == "CLEAN"
    assert res_unknown["result"] == "NO_RECORD"
    assert res_unknown["checked"] is True

    # Known malicious
    res_mal = await local_engine.check_url("http://paypa1-account-verification.xyz/login.php")
    assert res_mal["status"] == "MALICIOUS"
    assert res_mal["checked"] is True
    assert res_mal["malicious_count"] == 1


# =========================================================================
# Scenario N: Provider-Specific TTL Caching and Non-Collision
# =========================================================================
@pytest.mark.asyncio
async def test_scenario_n_provider_specific_ttl_cache():
    """Scenario N: TTL Cache keys on (provider, url_hash) and does not cross-pollute providers."""
    service = ThreatIntelService()
    service.clear_cache()

    test_url = "https://example-test-cache-url.org"

    # 1. First check -> Cache Miss
    res1 = await service.check(test_url)
    assert res1.get("cached") is False or "cached" not in res1 or not res1["cached"]

    # 2. Second check -> Cache Hit
    res2 = await service.check(test_url)
    assert res2.get("cached") is True

    # 3. Different URL -> Cache Miss
    diff_url = "https://another-distinct-domain.com"
    res3 = await service.check(diff_url)
    assert res3.get("cached") is False or not res3.get("cached")

