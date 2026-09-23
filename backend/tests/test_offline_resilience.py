"""
Tests for 100% Offline Capability and Air-Gapped Operation.
Ensures QRadar performs full heuristic, ML, threat intelligence, and persistence analysis
with zero internet connectivity.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.threat_intel import LocalOfflineThreatIntelProvider, threat_intel_service
from app.services.scan_service import scan_service


@pytest.mark.asyncio
async def test_offline_threat_intel_clean_and_malicious():
    provider = LocalOfflineThreatIntelProvider()

    # Test verified clean domain
    res_clean = await provider.check_url("https://www.google.com/search?q=test")
    assert res_clean["status"] == "CLEAN"
    assert "google.com" in res_clean["details"]

    # Test known malicious lookalike
    res_mal = await provider.check_url("http://paypa1-account-verification.xyz/login.php")
    assert res_mal["status"] == "MALICIOUS"
    assert "paypa1" in res_mal["details"].lower() or "blacklist" in res_mal["details"].lower()


@pytest.mark.asyncio
async def test_offline_threat_intel_service_fallback():
    # Threat intelligence service should immediately resolve via local offline engine
    res = await threat_intel_service.check("https://github.com/torvalds/linux")
    assert res["status"] in {"CLEAN", "NO_THREAT_FOUND", "NOT_FOUND"}
    assert "Local Threat Engine" in res["provider"]


@pytest.mark.asyncio
async def test_offline_full_pipeline_scan():
    # Complete scan without internet
    result = await scan_service.analyze_and_persist("https://paypal.com@evil-phishing-gate.ru/login", source="offline_test")
    assert result.verdict == "MALICIOUS"
    assert result.recommended_action == "BLOCK"
    assert result.risk_score >= 70
    assert result.threat_intelligence.provider is not None


@pytest.mark.asyncio
async def test_offline_static_assets_served():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Check static Chart.js
        resp_chart = await client.get("/static/js/chart.umd.min.js")
        assert resp_chart.status_code == 200
        assert len(resp_chart.content) > 1000

        # Check static jsQR
        resp_jsqr = await client.get("/static/js/jsqr.min.js")
        assert resp_jsqr.status_code == 200
        assert len(resp_jsqr.content) > 1000
