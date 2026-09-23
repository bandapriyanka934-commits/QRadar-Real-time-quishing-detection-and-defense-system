"""
Test runner for Section 14 verification test cases:
TEST 1: Normal HTTPS URL
TEST 2: Suspicious URL
TEST 3: javascript:alert(1)
TEST 4: UPI payload
TEST 5: ML model unavailable
TEST 6: Threat Intelligence unavailable
"""

import os
import sys
import json
import asyncio

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
ML_SRC_DIR = os.path.join(ROOT_DIR, "ml", "src")

for p in [ROOT_DIR, BACKEND_DIR, ML_SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.services.scan_service import scan_service
from app.services.ml_engine import MLEngineService
from app.services.threat_intel import VirusTotalProvider
from app.core.config import settings
from app.db.session import init_db, AsyncSessionLocal

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


async def run_tests():
    print("=" * 70)
    print("      QRADAR SECTION 14 VERIFICATION TEST SUITE")
    print("=" * 70)

    await init_db()

    async with AsyncSessionLocal() as db:
        # TEST 1: Normal HTTPS URL
        print("\n[TEST 1] Normal HTTPS URL (https://www.google.com)")
        res1 = await scan_service.analyze_and_persist("https://www.google.com", db=db, source="test_1")
        print(f"  Verdict: {res1.verdict}, Action: {res1.recommended_action}, Score: {res1.risk_score}")
        print(f"  ML: status={res1.ml.status}, prediction={res1.ml.prediction}, confidence={res1.ml.confidence}, model={res1.ml.model_name}")
        print(f"  TI: status={res1.threat_intelligence.status}, provider={res1.threat_intelligence.provider}")
        assert res1.verdict == "SAFE"
        assert res1.ml.status == "ANALYZED"
        assert res1.ml.prediction == "Legitimate"
        assert res1.threat_intelligence.status in ["NO_THREAT_FOUND", "CLEAN"]
        print("  [PASSED] Test 1 Succeeded")

        # TEST 2: Suspicious URL
        print("\n[TEST 2] Suspicious URL (http://paypa1-account-verification.xyz/login.php)")
        res2 = await scan_service.analyze_and_persist("http://paypa1-account-verification.xyz/login.php", db=db, source="test_2")
        print(f"  Verdict: {res2.verdict}, Action: {res2.recommended_action}, Score: {res2.risk_score}")
        print(f"  ML: status={res2.ml.status}, prediction={res2.ml.prediction}, prob={res2.ml.phishing_probability}")
        print(f"  TI: status={res2.threat_intelligence.status}, provider={res2.threat_intelligence.provider}")
        assert res2.verdict == "MALICIOUS"
        assert res2.recommended_action == "BLOCK"
        assert res2.ml.status == "ANALYZED"
        assert res2.ml.prediction == "Phishing"
        print("  [PASSED] Test 2 Succeeded")

        # TEST 3: javascript:alert(1)
        print("\n[TEST 3] Dangerous Scheme (javascript:alert(1))")
        res3 = await scan_service.analyze_and_persist("javascript:alert(1)", db=db, source="test_3")
        print(f"  Verdict: {res3.verdict}, Action: {res3.recommended_action}, Score: {res3.risk_score}")
        print(f"  ML: status={res3.ml.status}, reason={res3.ml.reason}")
        print(f"  TI: status={res3.threat_intelligence.status}, reason={res3.threat_intelligence.reason}")
        assert res3.verdict == "MALICIOUS"
        assert res3.recommended_action == "BLOCK"
        assert res3.risk_score >= 90
        assert res3.ml.status == "NOT_APPLICABLE"
        assert res3.threat_intelligence.status == "NOT_APPLICABLE"
        print("  [PASSED] Test 3 Succeeded")

        # TEST 4: UPI payload
        print("\n[TEST 4] UPI payload (upi://pay?pa=test@example&pn=DemoStore&am=250)")
        res4 = await scan_service.analyze_and_persist("upi://pay?pa=test@example&pn=DemoStore&am=250", db=db, source="test_4")
        print(f"  Verdict: {res4.verdict}, Action: {res4.recommended_action}, Score: {res4.risk_score}")
        print(f"  ML: status={res4.ml.status}, reason={res4.ml.reason}")
        print(f"  TI: status={res4.threat_intelligence.status}, reason={res4.threat_intelligence.reason}")
        assert res4.verdict == "SAFE"
        assert res4.recommended_action == "ALLOW"
        assert res4.ml.status == "NOT_APPLICABLE"
        assert res4.ml.reason == "Non-web QR payload"
        assert res4.threat_intelligence.status == "NOT_APPLICABLE"
        assert res4.threat_intelligence.reason == "No web URL/domain to check"
        print("  [PASSED] Test 4 Succeeded")

        # TEST 5: ML model unavailable
        print("\n[TEST 5] ML model unavailable (graceful degradation)")
        dummy_ml = MLEngineService(model_path="non_existent_model_file.joblib")
        dummy_pred = dummy_ml.predict("https://www.google.com")
        print(f"  ML Unavailable output: status={dummy_pred['status']}, reason={dummy_pred['reason']}")
        assert dummy_pred["available"] is False
        assert dummy_pred["status"] == "UNAVAILABLE"
        assert dummy_pred["prediction"] is None
        assert dummy_pred["reason"] is not None
        print("  [PASSED] Test 5 Succeeded (No fake predictions)")

        # TEST 6: Threat Intelligence unavailable / not configured
        print("\n[TEST 6] Threat Intelligence unavailable (API key unconfigured)")
        unconfigured_vt = VirusTotalProvider(api_key="")
        vt_res = await unconfigured_vt.check_url("https://www.google.com")
        print(f"  TI Output: status={vt_res['status']}, provider={vt_res['provider']}, error_reason={vt_res['error_reason']}")
        assert vt_res["status"] in {"NOT_AVAILABLE", "NOT_CONFIGURED", "UNAVAILABLE"}
        assert vt_res["provider"] == "VirusTotal"
        assert vt_res["checked"] is False
        assert vt_res["error_reason"] == "API_KEY_NOT_CONFIGURED"
        assert vt_res["malicious_count"] is None
        print("  [PASSED] Test 6 Succeeded (Truthful NOT_AVAILABLE status)")

    print("\n" + "=" * 70)
    print("🎉 ALL 6 SECTION 14 VERIFICATION TESTS PASSED PERFECTLY!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tests())
