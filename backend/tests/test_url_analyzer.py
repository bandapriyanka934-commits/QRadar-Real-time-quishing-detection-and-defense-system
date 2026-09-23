"""
Unit tests for URL Analyzer, Dangerous Scheme Rejection, and SSRF Guards.
"""

import pytest
from app.services.url_analyzer import url_analyzer_service, DANGEROUS_SCHEMES


def test_standard_https_url():
    res = url_analyzer_service.parse_and_normalize("https://www.google.com/search?q=cybersecurity")
    assert res.content_type == "url"
    assert res.scheme == "https"
    assert res.domain == "www.google.com"
    assert res.path == "/search"
    assert res.query == "q=cybersecurity"
    assert not res.is_dangerous_scheme
    assert not res.is_private_ip


def test_dangerous_schemes_rejection():
    schemes_to_test = [
        "javascript:alert(document.cookie)",
        "file:///etc/passwd",
        "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
        "blob:https://evil.com/123-456",
        "intent://scan/#Intent;scheme=zxing;package=com.google.zxing.client.android;end",
        "about:blank",
        "vbscript:msgbox(1)",
    ]

    for payload in schemes_to_test:
        res = url_analyzer_service.parse_and_normalize(payload)
        assert res.content_type == "dangerous_scheme", f"Failed for {payload}"
        assert res.is_dangerous_scheme is True
        assert res.danger_reason is not None


def test_plain_text_and_contact():
    text_payloads = [
        "Hello this is just a meeting note text.",
        "WIFI:S:MyNetwork;T:WPA;P:SecretPassword;;",
        "mailto:support@qradar.local",
        "tel:+1234567890",
    ]
    for text in text_payloads:
        res = url_analyzer_service.parse_and_normalize(text)
        assert res.content_type == "text"
        assert not res.is_dangerous_scheme


def test_private_and_loopback_ip_ssrf():
    private_urls = [
        "http://127.0.0.1:8080/admin",
        "http://192.168.1.1/router-login",
        "http://10.0.0.5/internal/dashboard",
        "http://172.16.0.2:3000/api",
        "http://169.254.169.254/latest/meta-data/",
    ]
    for url in private_urls:
        res = url_analyzer_service.parse_and_normalize(url)
        assert res.content_type == "url"
        assert res.is_private_ip is True, f"Failed to flag private IP for {url}"


def test_public_domain_not_private():
    res = url_analyzer_service.parse_and_normalize("https://github.com/torvalds/linux")
    assert res.content_type == "url"
    assert res.is_private_ip is False
