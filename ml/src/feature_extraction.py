"""
Feature extraction module for URL Phishing Classification.
This module is shared between the ML training pipeline and the production FastAPI backend.
All feature calculations must remain 100% deterministic and identical in both environments.
"""

import math
import re
import ipaddress
from urllib.parse import urlparse
from typing import Dict, List, Any


# Ordered list of feature names used by the model
FEATURE_NAMES: List[str] = [
    "url_length",
    "hostname_length",
    "path_length",
    "query_length",
    "num_dots",
    "num_hyphens",
    "num_underscores",
    "num_slashes",
    "num_question_marks",
    "num_equal_signs",
    "num_at_symbols",
    "num_percent_signs",
    "num_digits",
    "num_subdomains",
    "is_https",
    "has_ip_host",
    "num_sensitive_keywords",
    "shannon_entropy",
]

SENSITIVE_KEYWORDS = [
    "login", "signin", "bank", "account", "verify", "update", "secure",
    "wallet", "password", "confirm", "auth", "service", "support", "token",
    "recover", "billing", "validate", "portal", "security", "chase", "paypal",
    "appleid", "microsoft", "google", "netflix", "amazon", "binance", "coinbase"
]


def calculate_entropy(text: str) -> float:
    """Calculates the Shannon entropy of a string."""
    if not text:
        return 0.0
    length = len(text)
    freq: Dict[str, int] = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


def is_ip_address(hostname: str) -> bool:
    """Checks if hostname is an IPv4 or IPv6 address."""
    if not hostname:
        return False
    # Strip port if present
    host = hostname.split(":")[0].strip("[]")
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def count_subdomains(hostname: str) -> int:
    """Estimates the number of subdomain levels in a hostname."""
    if not hostname or is_ip_address(hostname):
        return 0
    parts = [p for p in hostname.split(".") if p]
    if len(parts) <= 2:
        return 0
    # For domains like example.co.uk or sub.example.com
    # Typical TLDs might take 1 or 2 parts
    tld_two_part_suffixes = {"co.uk", "gov.uk", "ac.uk", "com.au", "net.au", "co.in", "ac.in", "co.jp"}
    if len(parts) >= 3 and f"{parts[-2]}.{parts[-1]}".lower() in tld_two_part_suffixes:
        return max(0, len(parts) - 3)
    return max(0, len(parts) - 2)


def extract_url_features(url: str) -> Dict[str, Any]:
    """
    Extracts numerical features from a URL for ML classification.
    Returns a dictionary mapping feature names to their numerical values.
    """
    if not url:
        url = ""

    parsed = urlparse(url)
    # If scheme was missing, attempt parsing with default http
    if not parsed.scheme and not parsed.netloc:
        parsed = urlparse(f"http://{url}")

    hostname = (parsed.netloc or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    scheme = (parsed.scheme or "").lower()

    # Features computation
    url_len = len(url)
    host_len = len(hostname)
    path_len = len(path)
    query_len = len(query)

    num_dots = url.count(".")
    num_hyphens = url.count("-")
    num_underscores = url.count("_")
    num_slashes = url.count("/")
    num_question_marks = url.count("?")
    num_equal_signs = url.count("=")
    num_at_symbols = url.count("@")
    num_percent_signs = url.count("%")
    num_digits = sum(1 for c in url if c.isdigit())
    
    num_subdomains = count_subdomains(hostname)
    is_https = 1 if scheme == "https" else 0
    has_ip = 1 if is_ip_address(hostname) else 0

    # Sensitive keywords in path, query, or hostname
    lower_url = url.lower()
    num_keywords = sum(1 for kw in SENSITIVE_KEYWORDS if kw in lower_url)
    entropy = calculate_entropy(url)

    return {
        "url_length": url_len,
        "hostname_length": host_len,
        "path_length": path_len,
        "query_length": query_len,
        "num_dots": num_dots,
        "num_hyphens": num_hyphens,
        "num_underscores": num_underscores,
        "num_slashes": num_slashes,
        "num_question_marks": num_question_marks,
        "num_equal_signs": num_equal_signs,
        "num_at_symbols": num_at_symbols,
        "num_percent_signs": num_percent_signs,
        "num_digits": num_digits,
        "num_subdomains": num_subdomains,
        "is_https": is_https,
        "has_ip_host": has_ip,
        "num_sensitive_keywords": num_keywords,
        "shannon_entropy": entropy,
    }


def extract_features_vector(url: str) -> List[float]:
    """
    Extracts a feature vector as an ordered list of floats according to FEATURE_NAMES.
    Used directly as input for ML model prediction.
    """
    feats = extract_url_features(url)
    return [float(feats[k]) for k in FEATURE_NAMES]
