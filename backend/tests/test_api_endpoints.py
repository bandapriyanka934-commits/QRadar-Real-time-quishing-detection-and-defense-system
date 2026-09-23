"""
Integration tests for FastAPI REST Endpoints, UPI QR payloads, and Security States.
"""

import pytest
import io
import qrcode
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "ml_model_available" in data


@pytest.mark.asyncio
async def test_scan_url_endpoint_safe(client: AsyncClient):
    payload = {"url": "https://www.google.com/search?q=qradar", "source": "manual"}
    resp = await client.post("/api/v1/scan/url", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] in ["SAFE", "SUSPICIOUS"]
    assert data["risk_score"] < 50
    assert "scan_id" in data
    assert "reasons" in data
    assert len(data["heuristics"]) >= 12
    # Verify ML and Threat Intel responses
    assert data["ml"]["status"] == "ANALYZED"
    assert data["ml"]["prediction"] == "Legitimate"
    assert data["threat_intelligence"]["status"] in ["NO_THREAT_FOUND", "CLEAN"]


@pytest.mark.asyncio
async def test_scan_url_endpoint_dangerous_scheme(client: AsyncClient):
    payload = {"url": "javascript:alert(document.cookie)", "source": "manual"}
    resp = await client.post("/api/v1/scan/url", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "MALICIOUS"
    assert data["recommended_action"] == "BLOCK"
    assert data["risk_score"] >= 90
    assert data["ml"]["status"] == "NOT_APPLICABLE"
    assert data["threat_intelligence"]["status"] == "NOT_APPLICABLE"


@pytest.mark.asyncio
async def test_scan_url_endpoint_upi(client: AsyncClient):
    payload = {"url": "upi://pay?pa=merchant@upi&pn=DemoStore&am=150.00&cu=INR", "source": "manual"}
    resp = await client.post("/api/v1/scan/url", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "SAFE"
    assert data["recommended_action"] == "ALLOW"
    assert data["content_type"] == "upi"
    assert data["ml"]["status"] == "NOT_APPLICABLE"
    assert data["ml"]["reason"] == "Non-web QR payload"
    assert data["threat_intelligence"]["status"] == "NOT_APPLICABLE"
    assert data["threat_intelligence"]["reason"] == "No web URL/domain to check"


@pytest.mark.asyncio
async def test_scan_image_endpoint(client: AsyncClient):
    # Generate a real in-memory QR code image
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data("https://www.wikipedia.org")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    files = {"file": ("test_qr.png", img_bytes, "image/png")}
    resp = await client.post("/api/v1/scan/image", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "scan_id" in data
    assert data["verdict"] == "SAFE"


@pytest.mark.asyncio
async def test_history_and_dashboard_flow(client: AsyncClient):
    # 1. Perform a scan
    payload = {"url": "https://paypal.com-verify-account.security-update.xyz/login.php", "source": "camera"}
    scan_resp = await client.post("/api/v1/scan/url", json=payload)
    assert scan_resp.status_code == 200
    scan_id = scan_resp.json()["scan_id"]

    # 2. Retrieve history list
    hist_resp = await client.get("/api/v1/scans")
    assert hist_resp.status_code == 200
    items = hist_resp.json()
    assert len(items) >= 1
    assert any(item["scan_id"] == scan_id for item in items)

    # 3. Retrieve specific scan details
    detail_resp = await client.get(f"/api/v1/scans/{scan_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["scan_id"] == scan_id

    # 4. Check dashboard metrics
    dash_resp = await client.get("/api/v1/dashboard")
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_scans"] >= 1
    assert "verdict_counts" in dash_data
    assert "risk_distribution" in dash_data
