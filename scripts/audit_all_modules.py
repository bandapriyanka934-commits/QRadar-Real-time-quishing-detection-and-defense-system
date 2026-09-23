"""
Comprehensive Deep Audit Script for QRadar.
Tests every single module, service, function, and edge case from backend to frontend models.
"""

import os
import sys
import io
import json
import asyncio
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
ML_SRC_DIR = os.path.join(ROOT_DIR, "ml", "src")

for p in [ROOT_DIR, BACKEND_DIR, ML_SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Imports from app
from app.core.config import settings
from app.db.session import init_db, get_db, AsyncSessionLocal
from app.services.qr_decoder import qr_decoder_service
from app.services.url_analyzer import url_analyzer_service
from app.services.heuristic_engine import heuristic_engine, levenshtein_distance
from app.services.ml_engine import ml_engine_service
from app.services.threat_intel import threat_intel_service, LocalOfflineThreatIntelProvider
from app.services.risk_engine import risk_engine
from app.services.scan_service import scan_service
from feature_extraction import extract_features_vector, calculate_entropy, FEATURE_NAMES


# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def log_test(module_name: str, test_name: str, passed: bool, details: str = ""):
    icon = "[+]" if passed else "[-]"
    print(f"{icon} [{module_name}] {test_name}: {'PASSED' if passed else 'FAILED'} {f'({details})' if details else ''}")
    if not passed:
        raise AssertionError(f"Test '{test_name}' in module '{module_name}' failed: {details}")


async def audit_module_1_qr_decoder():
    print("\n--- Auditing Module 1: QR Decoder Service ---")
    
    # 1. Empty bytes
    res_empty = qr_decoder_service.decode_image_bytes(b"")
    log_test("QR Decoder", "Empty Bytes Handling", res_empty == [])

    # 2. Corrupted bytes
    try:
        qr_decoder_service.decode_image_bytes(b"not an image at all")
        log_test("QR Decoder", "Corrupted Image Detection", False, "Should raise ValueError")
    except ValueError:
        log_test("QR Decoder", "Corrupted Image Detection", True, "Raised ValueError as expected")

    # 3. Test on demo assets if present
    demo_dir = os.path.join(ROOT_DIR, "demo_assets")
    if os.path.exists(demo_dir):
        for img_name in sorted(os.listdir(demo_dir)):
            if img_name.endswith(".png"):
                img_path = os.path.join(demo_dir, img_name)
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                decoded = qr_decoder_service.decode_image_bytes(img_bytes)
                log_test("QR Decoder", f"Asset {img_name}", len(decoded) > 0, f"Decoded: {len(decoded)} QRs")


async def audit_module_2_url_analyzer():
    print("\n--- Auditing Module 2: URL Analyzer & Scheme Normalizer ---")
    
    # 1. Standard HTTPS URL
    p1 = url_analyzer_service.parse_and_normalize("https://www.google.com/search?q=quishing")
    log_test("URL Analyzer", "Standard HTTPS", p1.content_type == "url" and p1.scheme == "https" and p1.domain == "www.google.com")

    # 2. Dangerous Scheme: javascript:
    p2 = url_analyzer_service.parse_and_normalize("javascript:alert(document.cookie)")
    log_test("URL Analyzer", "Dangerous Scheme (javascript:)", p2.is_dangerous_scheme and p2.scheme == "javascript")

    # 3. Dangerous Scheme: file:, data:, blob:, intent:
    for d_scheme in ["file:///etc/passwd", "data:text/html;base64,PHNjcmlwdD4=", "blob:https://evil.com/uuid", "intent://scan/#Intent;"]:
        p = url_analyzer_service.parse_and_normalize(d_scheme)
        log_test("URL Analyzer", f"Dangerous Scheme ({d_scheme.split(':')[0]}:)", p.is_dangerous_scheme)

    # 4. UPI Payment Scheme
    p_upi = url_analyzer_service.parse_and_normalize("upi://pay?pa=merchant@upi&pn=DemoStore&am=100")
    log_test("URL Analyzer", "UPI Scheme Detection", p_upi.content_type == "upi" and p_upi.scheme == "upi" and p_upi.upi_params.get("pa") == "merchant@upi")

    # 5. Private / Loopback SSRF IPs
    p_priv1 = url_analyzer_service.parse_and_normalize("http://127.0.0.1:8000/admin")
    p_priv2 = url_analyzer_service.parse_and_normalize("http://192.168.1.1/setup")
    p_priv3 = url_analyzer_service.parse_and_normalize("http://10.0.0.5:8080/login")
    log_test("URL Analyzer", "Loopback 127.0.0.1 SSRF", p_priv1.is_private_ip)
    log_test("URL Analyzer", "Private 192.168.x.x SSRF", p_priv2.is_private_ip)
    log_test("URL Analyzer", "Private 10.x.x.x SSRF", p_priv3.is_private_ip)

    # 6. Public domain should NOT be private IP
    p_pub = url_analyzer_service.parse_and_normalize("https://www.google.com")
    log_test("URL Analyzer", "Public Domain Non-Private", not p_pub.is_private_ip)

    # 7. Plain text & contact schemes
    p_txt = url_analyzer_service.parse_and_normalize("Just a friendly meeting note at 3 PM")
    log_test("URL Analyzer", "Plain Text Detection", p_txt.content_type == "text" and p_txt.normalized_url is None)

    p_wifi = url_analyzer_service.parse_and_normalize("WIFI:S:GuestNetwork;T:WPA;P:SecretPass;;")
    log_test("URL Analyzer", "WIFI Scheme Handling", p_wifi.content_type == "text" and p_wifi.scheme == "wifi")


async def audit_module_3_heuristics():
    print("\n--- Auditing Module 3: 12+ Heuristic Detection Engine ---")

    # 1. Levenshtein Distance
    d1 = levenshtein_distance("paypal", "paypal")
    d2 = levenshtein_distance("paypal", "paypa1")
    d3 = levenshtein_distance("google", "g00gle")
    log_test("Heuristics", "Levenshtein Exact Match", d1 == 0)
    log_test("Heuristics", "Levenshtein 1-char substitution", d2 == 1)
    log_test("Heuristics", "Levenshtein 2-char substitution", d3 == 2)

    # 2. Test 12 individual checks on representative URLs
    # 2a. Lookalike typosquatting
    p_look = url_analyzer_service.parse_and_normalize("http://paypa1-security-verification.xyz/login")
    h_look = heuristic_engine.check_lookalike_typosquatting(p_look.domain)
    log_test("Heuristics", "Typosquatting Detection", h_look["triggered"], f"Evidence: {h_look['evidence']}")

    # 2b. Userinfo @ trick
    p_userinfo = url_analyzer_service.parse_and_normalize("https://paypal.com@evil-gate.ru/login")
    h_userinfo = heuristic_engine.check_userinfo_trick(p_userinfo.original_content)
    log_test("Heuristics", "Userinfo @ Trick", h_userinfo["triggered"])

    # 2c. Direct IP host
    p_ip = url_analyzer_service.parse_and_normalize("http://192.168.1.105:8080/login.htm")
    h_ip = heuristic_engine.check_ip_address_host(p_ip.hostname)
    log_test("Heuristics", "Direct IP Host", h_ip["triggered"])

    # 2d. Non-standard port
    h_port = heuristic_engine.check_suspicious_port(p_ip.port)
    log_test("Heuristics", "Non-Standard Port :8080", h_port["triggered"])

    # 2e. URL shortener
    p_short = url_analyzer_service.parse_and_normalize("http://bit.ly/3xSampleShortener")
    h_short = heuristic_engine.check_url_shortener(p_short.domain)
    log_test("Heuristics", "URL Shortener (bit.ly)", h_short["triggered"])

    # 2f. Punycode IDN
    p_puny = url_analyzer_service.parse_and_normalize("https://xn--pypal-4ve.com/login")
    h_puny = heuristic_engine.check_punycode_idn(p_puny.domain)
    log_test("Heuristics", "Punycode IDN (xn--)", h_puny["triggered"])

    # 2g. Suspicious keywords
    p_kw = url_analyzer_service.parse_and_normalize("http://legit-site.com/account/verify/password/recover")
    h_kw = heuristic_engine.check_suspicious_keywords(p_kw.normalized_url)
    log_test("Heuristics", "Suspicious Keywords", h_kw["triggered"])

    # 2h. Full 12-indicator evaluation
    eval_all = heuristic_engine.evaluate_all(p_look.normalized_url, p_look)
    log_test("Heuristics", "Full 12 Indicators Returned", len(eval_all) == 12)


async def audit_module_4_ml_engine():
    print("\n--- Auditing Module 4: ML Phishing Detection Engine ---")

    # 1. Entropy calculation
    ent_simple = calculate_entropy("aaaaaa")
    ent_random = calculate_entropy("aX9@kQ2#zL")
    log_test("ML Engine", "Entropy Simple vs High", ent_simple == 0.0 and ent_random > 3.0)

    # 2. Feature Extraction Vector
    vec = extract_features_vector("http://paypa1-verify.xyz/login.php?user=admin")
    log_test("ML Engine", "18-Feature Vector Length", len(vec) == 18 and len(FEATURE_NAMES) == 18)

    # 3. Model availability
    log_test("ML Engine", "Model Singleton Loaded", ml_engine_service.is_available)

    # 4. Phishing URL prediction
    pred_phish = ml_engine_service.predict("http://paypa1-account-verify.xyz/login.php?credential=recover")
    log_test("ML Engine", "Phishing Prediction (>0.70)", pred_phish["phishing_probability"] is not None and pred_phish["phishing_probability"] > 0.70 and pred_phish["prediction"] == "Phishing", f"Prob: {pred_phish['phishing_probability']}")

    # 5. Benign URL prediction
    pred_safe = ml_engine_service.predict("https://www.google.com")
    log_test("ML Engine", "Benign Prediction (<0.50, Legitimate)", pred_safe["phishing_probability"] is not None and pred_safe["phishing_probability"] < 0.50 and pred_safe["prediction"] == "Legitimate", f"Prob: {pred_safe['phishing_probability']}")

    # 6. Not Applicable handling
    na_res = ml_engine_service.not_applicable(reason="Non-web QR payload")
    log_test("ML Engine", "Not Applicable Status", na_res["status"] == "NOT_APPLICABLE" and na_res["available"] is False)


async def audit_module_5_threat_intel():
    print("\n--- Auditing Module 5: Threat Intelligence Layer ---")

    offline_prov = LocalOfflineThreatIntelProvider()

    # 1. Known malicious domain
    ti_mal = await offline_prov.check_url("http://paypa1-account-verification.xyz/login.php")
    log_test("Threat Intel", "Offline Blacklist Match", ti_mal["status"] == "MALICIOUS")

    # 2. Verified clean domain
    ti_clean = await offline_prov.check_url("https://www.google.com")
    log_test("Threat Intel", "Offline Whitelist Match", ti_clean["status"] == "CLEAN")

    # 3. Unknown neutral domain
    ti_neutral = await offline_prov.check_url("https://random-unknown-domain-test123.com")
    log_test("Threat Intel", "Offline Unknown Domain", ti_neutral["status"] == "CLEAN" and ti_neutral["result"] == "NO_RECORD")

    # 4. Service Orchestrator
    ti_service_res = await threat_intel_service.check("https://github.com")
    log_test("Threat Intel", "ThreatIntelService Result", ti_service_res["status"] == "CLEAN")

    # 5. Not Applicable handling
    na_ti = threat_intel_service.not_applicable(reason="No web URL/domain to check")
    log_test("Threat Intel", "Not Applicable Status", na_ti["status"] == "NOT_APPLICABLE" and na_ti["reason"] == "No web URL/domain to check")


async def audit_module_6_risk_engine():
    print("\n--- Auditing Module 6: Unified Risk Engine ---")

    # 1. Dangerous scheme override -> BLOCK
    p_dang = url_analyzer_service.parse_and_normalize("javascript:alert(1)")
    r_dang = risk_engine.evaluate(p_dang, [], {"available": False, "status": "NOT_APPLICABLE"}, {"status": "NOT_APPLICABLE"})
    log_test("Risk Engine", "Dangerous Scheme Forced Block", r_dang["verdict"] == "MALICIOUS" and r_dang["recommended_action"] == "BLOCK" and r_dang["risk_score"] >= 95)

    # 2. UPI Payload -> SAFE / ALLOW
    p_upi = url_analyzer_service.parse_and_normalize("upi://pay?pa=test@upi&pn=Store&am=100")
    r_upi = risk_engine.evaluate(p_upi, [], {"available": False, "status": "NOT_APPLICABLE"}, {"status": "NOT_APPLICABLE"})
    log_test("Risk Engine", "UPI Payload Safe Evaluation", r_upi["verdict"] == "SAFE" and r_upi["recommended_action"] == "ALLOW")

    # 3. Plain text -> SAFE / ALLOW
    p_text = url_analyzer_service.parse_and_normalize("Meeting at 5pm in lobby")
    r_text = risk_engine.evaluate(p_text, [], {"available": False, "status": "NOT_APPLICABLE"}, {"status": "NOT_APPLICABLE"})
    log_test("Risk Engine", "Plain Text Forced Safe", r_text["verdict"] == "SAFE" and r_text["recommended_action"] == "ALLOW" and r_text["risk_score"] <= 15)

    # 4. Clean domain -> SAFE / ALLOW
    p_google = url_analyzer_service.parse_and_normalize("https://www.google.com/search?q=test")
    h_google = heuristic_engine.evaluate_all(p_google.normalized_url, p_google)
    ml_google = ml_engine_service.predict(p_google.normalized_url)
    ti_google = await threat_intel_service.check(p_google.normalized_url)
    r_google = risk_engine.evaluate(p_google, h_google, ml_google, ti_google)
    log_test("Risk Engine", "Google Clean Evaluation", r_google["verdict"] == "SAFE" and r_google["risk_score"] < 30)

    # 5. Typosquat Phish -> MALICIOUS / BLOCK
    p_phish = url_analyzer_service.parse_and_normalize("http://paypa1-account-verification.xyz/login.php")
    h_phish = heuristic_engine.evaluate_all(p_phish.normalized_url, p_phish)
    ml_phish = ml_engine_service.predict(p_phish.normalized_url)
    ti_phish = await threat_intel_service.check(p_phish.normalized_url)
    r_phish = risk_engine.evaluate(p_phish, h_phish, ml_phish, ti_phish)
    log_test("Risk Engine", "Phishing Evaluation", r_phish["verdict"] == "MALICIOUS" and r_phish["risk_score"] >= 70)


async def audit_module_7_persistence_and_dashboard():
    print("\n--- Auditing Module 7: SQLite Persistence & Dashboard Analytics ---")

    await init_db()

    async with AsyncSessionLocal() as db:
        # 1. Persist scan
        res1 = await scan_service.analyze_and_persist("https://www.google.com", db=db, source="audit_test")
        log_test("Persistence", "Scan Persisted", res1.scan_id is not None and res1.verdict == "SAFE")

        # 2. Retrieve scan
        retrieved = await scan_service.get_scan_by_id(db, res1.scan_id)
        log_test("Persistence", "Get Scan by ID", retrieved is not None and retrieved.scan_id == res1.scan_id)

        # 3. Query history list
        history = await scan_service.get_history(db, limit=10)
        log_test("Persistence", "Get Scan History List", len(history) > 0)

        # 4. Get Dashboard statistics
        dash = await scan_service.get_dashboard_metrics(db)
        log_test("Persistence", "Dashboard Stats Computed", dash.total_scans > 0 and dash.verdict_counts.safe > 0)


async def main():
    print("=" * 70)
    print("      QRADAR SYSTEM-WIDE ALL MODULE AUDIT & VALIDATION")
    print("=" * 70)

    try:
        await audit_module_1_qr_decoder()
        await audit_module_2_url_analyzer()
        await audit_module_3_heuristics()
        await audit_module_4_ml_engine()
        await audit_module_5_threat_intel()
        await audit_module_6_risk_engine()
        await audit_module_7_persistence_and_dashboard()
        
        print("\n" + "=" * 70)
        print("🎉 ALL QRADAR MODULES AUDITED AND VERIFIED 100% OPERATIONAL!")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ AUDIT FAILED WITH ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
