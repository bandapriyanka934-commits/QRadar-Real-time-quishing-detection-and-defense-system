"""
Unit tests for Unified Risk Engine scoring, verdicts, boundary thresholds, and precedence rules.
"""

import pytest
from app.services.risk_engine import risk_engine
from app.services.url_analyzer import ParsedContent


def test_dangerous_scheme_forces_block():
    """Deterministic Precedence: Dangerous schemes force score 98 and BLOCK verdict."""
    dangerous_schemes = ["javascript", "file", "data", "blob", "intent", "about", "vbscript", "content"]
    for scheme in dangerous_schemes:
        parsed = ParsedContent(
            content_type="dangerous_scheme",
            original_content=f"{scheme}:doSomething()",
            scheme=scheme,
            is_dangerous_scheme=True,
            danger_reason=f"Dangerous {scheme} scheme"
        )
        res = risk_engine.evaluate(
            parsed=parsed,
            heuristics=[],
            ml_result={"available": True, "phishing_probability": 0.01},  # low ML must not override
            threat_intel={"status": "CLEAN"}                             # clean TI must not override
        )
        assert res["verdict"] == "MALICIOUS"
        assert res["recommended_action"] == "BLOCK"
        assert res["risk_score"] == 98


def test_plain_text_safe():
    """Plain text payloads evaluate to SAFE."""
    parsed = ParsedContent(
        content_type="text",
        original_content="Hello world! This is contact text.",
    )
    res = risk_engine.evaluate(parsed=parsed, heuristics=[], ml_result={}, threat_intel={})
    assert res["verdict"] == "SAFE"
    assert res["recommended_action"] == "ALLOW"
    assert res["risk_score"] <= 29


def test_threat_intel_malicious_forces_block():
    """Deterministic Precedence: Confirmed MALICIOUS threat intelligence forces BLOCK."""
    parsed = ParsedContent(
        content_type="url",
        original_content="https://malicious-sample.org",
        normalized_url="https://malicious-sample.org",
        domain="malicious-sample.org",
        scheme="https"
    )
    threat = {
        "status": "MALICIOUS",
        "provider": "Google Safe Browsing",
        "details": "Confirmed Phishing Feed Hit"
    }
    # Even if ML returned low probability (e.g. 0.05), confirmed TI forces BLOCK
    res = risk_engine.evaluate(
        parsed=parsed,
        heuristics=[],
        ml_result={"available": True, "phishing_probability": 0.05, "status": "ANALYZED"},
        threat_intel=threat
    )
    assert res["verdict"] == "MALICIOUS"
    assert res["recommended_action"] == "BLOCK"
    assert res["risk_score"] >= 70


def test_clean_url_safe():
    """Verified clean URL with no heuristic flags evaluates to SAFE."""
    parsed = ParsedContent(
        content_type="url",
        original_content="https://github.com/torvalds/linux",
        normalized_url="https://github.com/torvalds/linux",
        domain="github.com",
        scheme="https"
    )
    heuristics = [
        {"indicator": "HTTPS_CHECK", "triggered": False, "score_contribution": 0, "explanation": "Secure"},
        {"indicator": "IP_ADDRESS_HOST", "triggered": False, "score_contribution": 0, "explanation": "Clean"}
    ]
    ml = {"available": True, "phishing_probability": 0.02, "status": "ANALYZED"}
    threat = {"status": "CLEAN", "provider": "Local Threat Engine"}

    res = risk_engine.evaluate(parsed=parsed, heuristics=heuristics, ml_result=ml, threat_intel=threat)
    assert res["verdict"] == "SAFE"
    assert res["recommended_action"] == "ALLOW"
    assert res["risk_score"] <= 29


def test_strong_heuristics_override_low_ml():
    """Deterministic Precedence: High heuristic evidence cannot be overridden by low ML prob."""
    parsed = ParsedContent(
        content_type="url",
        original_content="https://paypal.com@evil-gate.ru/login",
        normalized_url="https://paypal.com@evil-gate.ru/login",
        domain="evil-gate.ru",
        scheme="https"
    )
    heuristics = [
        {"indicator": "USERINFO_TRICK", "triggered": True, "score_contribution": 40, "explanation": "Userinfo trick"},
        {"indicator": "LOOKALIKE_TYPOSQUATTING", "triggered": True, "score_contribution": 35, "explanation": "Lookalike"}
    ]
    # ML gives low probability
    ml = {"available": True, "phishing_probability": 0.10, "status": "ANALYZED"}
    threat = {"status": "CLEAN", "provider": "Mock"}

    res = risk_engine.evaluate(parsed=parsed, heuristics=heuristics, ml_result=ml, threat_intel=threat)
    assert res["verdict"] in {"SUSPICIOUS", "MALICIOUS"}
    assert res["risk_score"] >= 50
    assert res["recommended_action"] in {"WARN", "BLOCK"}


def test_private_ip_ssrf_target_blocked():
    """SSRF / Private IP target raises risk score >= 75."""
    parsed = ParsedContent(
        content_type="url",
        original_content="http://192.168.1.1/admin",
        normalized_url="http://192.168.1.1/admin",
        domain="192.168.1.1",
        hostname="192.168.1.1",
        scheme="http",
        is_private_ip=True
    )
    res = risk_engine.evaluate(
        parsed=parsed,
        heuristics=[],
        ml_result={"available": False, "status": "NOT_APPLICABLE"},
        threat_intel={"status": "CLEAN"}
    )
    assert res["verdict"] == "MALICIOUS"
    assert res["recommended_action"] == "BLOCK"
    assert res["risk_score"] >= 70


def test_exact_risk_boundary_thresholds():
    """
    Requirement 7 Boundary Verification:
      0 - 29   -> SAFE       / ALLOW
      30 - 69  -> SUSPICIOUS / WARN
      70 - 100 -> MALICIOUS  / BLOCK
    """
    parsed = ParsedContent(content_type="url", original_content="https://test.com", domain="test.com", scheme="https")

    # 1. Boundary 29 -> SAFE
    # 29 heuristics points with ML=0, TI neutral
    res_29 = risk_engine.evaluate(
        parsed=parsed,
        heuristics=[{"indicator": "TEST", "triggered": True, "score_contribution": 29, "explanation": "Test 29"}],
        ml_result={"available": True, "status": "ANALYZED", "phishing_probability": 0.0},
        threat_intel={"status": "NOT_APPLICABLE"}
    )
    assert res_29["risk_score"] == 29
    assert res_29["verdict"] == "SAFE"
    assert res_29["recommended_action"] == "ALLOW"

    # 2. Boundary 30 -> SUSPICIOUS
    res_30 = risk_engine.evaluate(
        parsed=parsed,
        heuristics=[{"indicator": "TEST", "triggered": True, "score_contribution": 30, "explanation": "Test 30"}],
        ml_result={"available": True, "status": "ANALYZED", "phishing_probability": 0.0},
        threat_intel={"status": "NOT_APPLICABLE"}
    )
    assert res_30["risk_score"] == 30
    assert res_30["verdict"] == "SUSPICIOUS"
    assert res_30["recommended_action"] == "WARN"

    # 3. Boundary 69 -> SUSPICIOUS
    # 44 heuristic points + ML prob 0.7142 (25 points) = 69
    res_69 = risk_engine.evaluate(
        parsed=parsed,
        heuristics=[{"indicator": "TEST", "triggered": True, "score_contribution": 44, "explanation": "Test 44"}],
        ml_result={"available": True, "status": "ANALYZED", "phishing_probability": 25.0 / 35.0},
        threat_intel={"status": "NOT_APPLICABLE"}
    )
    assert res_69["risk_score"] == 69
    assert res_69["verdict"] == "SUSPICIOUS"
    assert res_69["recommended_action"] == "WARN"

    # 4. Boundary 70 -> MALICIOUS
    # 35 heuristic points + ML prob 1.0 (35 points) = 70
    res_70 = risk_engine.evaluate(
        parsed=parsed,
        heuristics=[{"indicator": "TEST", "triggered": True, "score_contribution": 35, "explanation": "Test 35"}],
        ml_result={"available": True, "status": "ANALYZED", "phishing_probability": 1.0},
        threat_intel={"status": "NOT_APPLICABLE"}
    )
    assert res_70["risk_score"] == 70
    assert res_70["verdict"] == "MALICIOUS"
    assert res_70["recommended_action"] == "BLOCK"

