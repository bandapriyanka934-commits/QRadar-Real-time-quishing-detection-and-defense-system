"""
Live API Server verification test script.
Starts uvicorn background instance or runs tests against FastAPI app.
"""

import sys
import os
import httpx
from starlette.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in [BACKEND_DIR, ROOT_DIR, os.path.join(ROOT_DIR, "ml", "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.main import app

def test_live_fastapi_endpoints():
    print("Testing FastAPI endpoints using TestClient...")
    with TestClient(app) as client:
        # 1. Health Check
        r = client.get("/health")
        assert r.status_code == 200
        print(f"  [+] GET /health -> {r.json()}")

        # 2. URL Scan
        r = client.post("/api/v1/scan/url", json={"url": "https://www.google.com", "source": "test"})
        assert r.status_code == 200
        print(f"  [+] POST /api/v1/scan/url (Google) -> Verdict: {r.json()['verdict']}, Risk: {r.json()['risk_score']}")

        # 3. Phishing Scan
        r = client.post("/api/v1/scan/url", json={"url": "http://paypa1-verify.xyz/login", "source": "test"})
        assert r.status_code == 200
        print(f"  [+] POST /api/v1/scan/url (PayPa1 Phish) -> Verdict: {r.json()['verdict']}, Risk: {r.json()['risk_score']}")

        # 4. Dangerous Scheme
        r = client.post("/api/v1/scan/url", json={"url": "javascript:alert(1)", "source": "test"})
        assert r.status_code == 200
        print(f"  [+] POST /api/v1/scan/url (javascript:) -> Verdict: {r.json()['verdict']}, Action: {r.json()['recommended_action']}")

        # 5. Dashboard
        r = client.get("/api/v1/dashboard")
        assert r.status_code == 200
        print(f"  [+] GET /api/v1/dashboard -> Total Scans: {r.json()['total_scans']}")

    print("\n>>> All FastAPI REST endpoints verified successfully! <<<\n")

if __name__ == "__main__":
    test_live_fastapi_endpoints()
