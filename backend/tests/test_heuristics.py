"""
Unit tests for all 12 Heuristic Engine indicators and Typosquatting detection.
"""

import pytest
from app.services.heuristic_engine import heuristic_engine, levenshtein_distance
from app.services.url_analyzer import url_analyzer_service


def test_levenshtein_distance():
    assert levenshtein_distance("paypal", "paypal") == 0
    assert levenshtein_distance("paypal", "paypa1") == 1
    assert levenshtein_distance("google", "g00gle") == 2
    assert levenshtein_distance("chase", "chse") == 1


def test_https_check():
    http_res = heuristic_engine.check_https("http")
    assert http_res["triggered"] is True
    assert http_res["indicator"] == "HTTPS_CHECK"

    https_res = heuristic_engine.check_https("https")
    assert https_res["triggered"] is False


def test_ip_address_host():
    ip_res = heuristic_engine.check_ip_address_host("192.168.1.1:8080")
    assert ip_res["triggered"] is True
    assert ip_res["severity"] == "HIGH"

    domain_res = heuristic_engine.check_ip_address_host("www.paypal.com")
    assert domain_res["triggered"] is False


def test_url_shortener():
    short_res = heuristic_engine.check_url_shortener("bit.ly")
    assert short_res["triggered"] is True

    tiny_res = heuristic_engine.check_url_shortener("tinyurl.com")
    assert tiny_res["triggered"] is True

    normal_res = heuristic_engine.check_url_shortener("stackoverflow.com")
    assert normal_res["triggered"] is False


def test_userinfo_trick():
    userinfo_res = heuristic_engine.check_userinfo_trick("https://google.com@evil-phish.ru/login")
    assert userinfo_res["triggered"] is True
    assert userinfo_res["severity"] == "CRITICAL"

    normal_res = heuristic_engine.check_userinfo_trick("https://google.com/search")
    assert normal_res["triggered"] is False


def test_excessive_subdomains():
    deep_res = heuristic_engine.check_excessive_subdomains("login.secure.bank.verify.account.phish.com")
    assert deep_res["triggered"] is True

    normal_res = heuristic_engine.check_excessive_subdomains("www.apple.com")
    assert normal_res["triggered"] is False


def test_unusual_length():
    long_url = "https://example.com/" + "a" * 150
    long_res = heuristic_engine.check_unusual_length(long_url)
    assert long_res["triggered"] is True

    normal_res = heuristic_engine.check_unusual_length("https://example.com/login")
    assert normal_res["triggered"] is False


def test_excessive_special_chars():
    spec_url = "https://phish.com/auth?token=123&session_id=abc-xyz_99%20&user=@test"
    spec_res = heuristic_engine.check_excessive_special_chars(spec_url)
    assert spec_res["triggered"] is True


def test_suspicious_encoding():
    enc_res = heuristic_engine.check_suspicious_encoding("http://bank.com/%2520login%2e%2e/admin")
    assert enc_res["triggered"] is True

    clean_res = heuristic_engine.check_suspicious_encoding("http://bank.com/login")
    assert clean_res["triggered"] is False


def test_suspicious_port():
    port_res = heuristic_engine.check_suspicious_port(8080)
    assert port_res["triggered"] is True

    std_res = heuristic_engine.check_suspicious_port(443)
    assert std_res["triggered"] is False


def test_punycode_idn():
    puny_res = heuristic_engine.check_punycode_idn("xn--pypal-4qa.com")
    assert puny_res["triggered"] is True

    clean_res = heuristic_engine.check_punycode_idn("paypal.com")
    assert clean_res["triggered"] is False


def test_suspicious_keywords():
    kw_url = "http://phish.xyz/login/verify-security/account-update"
    kw_res = heuristic_engine.check_suspicious_keywords(kw_url)
    assert kw_res["triggered"] is True


def test_lookalike_typosquatting():
    # 1. Lookalike domain
    typo_res = heuristic_engine.check_lookalike_typosquatting("paypa1.com")
    assert typo_res["triggered"] is True
    assert "PayPal" in typo_res["explanation"]

    # 2. Combo-squatting
    combo_res = heuristic_engine.check_lookalike_typosquatting("paypal-security-update.com")
    assert combo_res["triggered"] is True

    # 3. Legitimate brand domain must NOT trigger
    legit_res = heuristic_engine.check_lookalike_typosquatting("paypal.com")
    assert legit_res["triggered"] is False

    legit_sub_res = heuristic_engine.check_lookalike_typosquatting("accounts.google.com")
    assert legit_sub_res["triggered"] is False
