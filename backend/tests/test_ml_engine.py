"""
Unit tests for Machine Learning feature extraction, model inference, and state handling.
"""

import pytest
from feature_extraction import extract_url_features, extract_features_vector, FEATURE_NAMES, calculate_entropy
from app.services.ml_engine import ml_engine_service


def test_calculate_entropy():
    assert calculate_entropy("") == 0.0
    assert calculate_entropy("aaaaaa") == 0.0
    ent = calculate_entropy("abcdef123456!@#$%")
    assert ent > 3.0


def test_feature_extraction_vector_shape():
    url = "https://www.google.com/search?q=test"
    feats = extract_url_features(url)
    assert len(feats) == len(FEATURE_NAMES)
    for name in FEATURE_NAMES:
        assert name in feats

    vec = extract_features_vector(url)
    assert len(vec) == len(FEATURE_NAMES)
    assert all(isinstance(v, (int, float)) for v in vec)


def test_ml_model_inference():
    if not ml_engine_service.is_available:
        pytest.skip("ML model artifact not loaded.")

    # Benign URL
    benign_res = ml_engine_service.predict("https://www.google.com/search?q=cybersecurity")
    assert benign_res["available"] is True
    assert benign_res["status"] == "ANALYZED"
    assert benign_res["prediction"] == "Legitimate"
    assert benign_res["confidence"] is not None
    assert benign_res["phishing_probability"] < 0.40

    # Phishing URL
    phish_res = ml_engine_service.predict("http://paypal.com-verify-account.security-update.xyz/login.php?user=123")
    assert phish_res["available"] is True
    assert phish_res["status"] == "ANALYZED"
    assert phish_res["prediction"] == "Phishing"
    assert phish_res["confidence"] is not None
    assert phish_res["phishing_probability"] > 0.60


def test_ml_not_applicable():
    na_res = ml_engine_service.not_applicable(reason="Non-web QR payload")
    assert na_res["available"] is False
    assert na_res["status"] == "NOT_APPLICABLE"
    assert na_res["prediction"] is None
    assert na_res["reason"] == "Non-web QR payload"
