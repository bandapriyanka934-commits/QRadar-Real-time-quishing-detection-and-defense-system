"""
Modular Heuristic Detection Engine for QRadar.
Executes 12+ deterministic security checks, including Levenshtein-distance brand typosquatting.
Each heuristic provides transparent indicators, severity levels, point contributions, and evidence.
"""

import re
import ipaddress
from urllib.parse import urlparse, unquote
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher

# Known URL shorteners
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "ow.ly", "cutt.ly", "buff.ly",
    "tiny.cc", "rebrand.ly", "shorte.st", "clck.ru", "adf.ly", "bit.do",
    "shorturl.at", "soo.gd", "s.id", "rb.gy", "qr.ae", "linktr.ee", "v.gd"
}

# Top targeted brands for typosquatting / lookalike detection
TARGET_BRANDS = [
    {"name": "PayPal", "domains": ["paypal.com", "paypal.me"]},
    {"name": "Google", "domains": ["google.com", "accounts.google.com", "gmail.com"]},
    {"name": "Apple", "domains": ["apple.com", "icloud.com", "appleid.apple.com"]},
    {"name": "Microsoft", "domains": ["microsoft.com", "live.com", "office.com", "outlook.com"]},
    {"name": "Amazon", "domains": ["amazon.com", "amazon.co.uk", "amazon.de"]},
    {"name": "Netflix", "domains": ["netflix.com"]},
    {"name": "Chase Bank", "domains": ["chase.com"]},
    {"name": "Bank of America", "domains": ["bankofamerica.com", "bofa.com"]},
    {"name": "Wells Fargo", "domains": ["wellsfargo.com"]},
    {"name": "Meta / Facebook", "domains": ["facebook.com", "fb.com", "meta.com"]},
    {"name": "Instagram", "domains": ["instagram.com"]},
    {"name": "WhatsApp", "domains": ["whatsapp.com"]},
    {"name": "Telegram", "domains": ["telegram.org", "t.me"]},
    {"name": "Binance", "domains": ["binance.com"]},
    {"name": "Coinbase", "domains": ["coinbase.com"]},
    {"name": "MetaMask", "domains": ["metamask.io"]},
    {"name": "Stripe", "domains": ["stripe.com"]},
    {"name": "eBay", "domains": ["ebay.com"]},
    {"name": "Dropbox", "domains": ["dropbox.com"]},
    {"name": "DHL Express", "domains": ["dhl.com", "dhl.de"]},
    {"name": "FedEx", "domains": ["fedex.com"]},
    {"name": "USPS", "domains": ["usps.com"]},
]

SUSPICIOUS_PATH_KEYWORDS = [
    "login", "signin", "verify", "verification", "secure", "security",
    "banking", "account", "update", "confirm", "confirmation", "recover",
    "password", "auth", "authorize", "authenticate", "billing", "validate",
    "unlock", "re-auth", "support-ticket", "credential", "session-id", "wallet"
]

NON_STANDARD_WEB_PORTS = {
    8080, 8443, 8888, 8000, 3000, 5000, 4444, 2082, 2083, 2086, 2087, 7080, 8088, 9090, 6666, 6667
}


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes exact Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def extract_base_domain(hostname: str) -> str:
    """Extracts the registered domain / base hostname without common subdomains."""
    if not hostname:
        return ""
    host = hostname.lower().split(":")[0].strip("[]")
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    # Handle two-part TLDs like co.uk, com.au
    two_part_tlds = {"co.uk", "gov.uk", "ac.uk", "com.au", "net.au", "co.in", "ac.in", "co.jp"}
    if len(parts) >= 3 and f"{parts[-2]}.{parts[-1]}" in two_part_tlds:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


class HeuristicEngine:
    """
    Modular, deterministic Heuristic Detection Engine.
    Evaluates 12 distinct security rules and scores each indicator.
    """

    def check_https(self, scheme: str) -> Dict[str, Any]:
        """Indicator 1: HTTPS Check."""
        is_https = (scheme or "").lower() == "https"
        return {
            "indicator": "HTTPS_CHECK",
            "name": "Transport Encryption (HTTPS)",
            "triggered": not is_https,
            "severity": "LOW" if not is_https else "LOW",
            "score_contribution": 10 if not is_https else 0,
            "explanation": "URL uses unencrypted HTTP communication, exposing data in transit." if not is_https else "URL uses secure TLS/HTTPS protocol.",
            "evidence": f"scheme: {scheme}" if scheme else "No scheme specified"
        }

    def check_ip_address_host(self, hostname: str) -> Dict[str, Any]:
        """Indicator 2: IP Address Hostname Detection."""
        if not hostname:
            return {
                "indicator": "IP_ADDRESS_HOST",
                "name": "Raw IP Hostname",
                "triggered": False,
                "severity": "HIGH",
                "score_contribution": 0,
                "explanation": "Destination uses a registered domain name.",
                "evidence": None
            }
        
        host_clean = hostname.split(":")[0].strip("[]")
        is_ip = False
        try:
            ipaddress.ip_address(host_clean)
            is_ip = True
        except ValueError:
            is_ip = False

        return {
            "indicator": "IP_ADDRESS_HOST",
            "name": "Raw IP Hostname",
            "triggered": is_ip,
            "severity": "HIGH" if is_ip else "LOW",
            "score_contribution": 35 if is_ip else 0,
            "explanation": f"Destination points directly to a raw IP address ({host_clean}) instead of a trusted domain." if is_ip else "Destination uses a registered domain name.",
            "evidence": host_clean if is_ip else None
        }

    def check_url_shortener(self, hostname: str) -> Dict[str, Any]:
        """Indicator 3: Known URL Shortener Detection."""
        host = (hostname or "").lower().split(":")[0]
        base = extract_base_domain(host)
        is_shortener = host in URL_SHORTENERS or base in URL_SHORTENERS

        return {
            "indicator": "URL_SHORTENER",
            "name": "URL Shortener Cloaking",
            "triggered": is_shortener,
            "severity": "MEDIUM" if is_shortener else "LOW",
            "score_contribution": 20 if is_shortener else 0,
            "explanation": f"Domain '{host}' is a known URL shortening service that conceals the true destination." if is_shortener else "Direct domain path (not a known URL shortener).",
            "evidence": host if is_shortener else None
        }

    def check_userinfo_trick(self, url: str) -> Dict[str, Any]:
        """Indicator 4: @ Symbol / Credential Userinfo Trick."""
        parsed = urlparse(url)
        has_at = "@" in url
        has_userinfo = bool(parsed.username or parsed.password or ("@" in parsed.netloc))

        triggered = has_at or has_userinfo
        evidence = parsed.netloc if triggered else None

        return {
            "indicator": "USERINFO_TRICK",
            "name": "Misleading '@' Credential Authority",
            "triggered": triggered,
            "severity": "CRITICAL" if triggered else "LOW",
            "score_contribution": 40 if triggered else 0,
            "explanation": "URL contains an '@' user-info symbol, commonly used to trick users into misreading the real host." if triggered else "URL authority structure is standard.",
            "evidence": evidence
        }

    def check_excessive_subdomains(self, hostname: str) -> Dict[str, Any]:
        """Indicator 5: Excessive Subdomains (> 3 levels)."""
        if not hostname:
            return {
                "indicator": "EXCESSIVE_SUBDOMAINS",
                "name": "Subdomain Depth",
                "triggered": False,
                "severity": "MEDIUM",
                "score_contribution": 0,
                "explanation": "Subdomain depth is within normal limits.",
                "evidence": None
            }
        
        host_clean = hostname.split(":")[0].strip("[]")
        parts = [p for p in host_clean.split(".") if p]
        subdomain_count = max(0, len(parts) - 2)
        triggered = subdomain_count >= 3

        return {
            "indicator": "EXCESSIVE_SUBDOMAINS",
            "name": "Subdomain Depth",
            "triggered": triggered,
            "severity": "MEDIUM" if triggered else "LOW",
            "score_contribution": 20 if triggered else 0,
            "explanation": f"Domain contains {subdomain_count} nested subdomain levels, often used to simulate brand domains." if triggered else "Subdomain depth is within standard bounds.",
            "evidence": f"{subdomain_count} subdomains ({host_clean})" if triggered else None
        }

    def check_unusual_length(self, url: str) -> Dict[str, Any]:
        """Indicator 6: Unusually Long URL (> 75 chars / > 120 chars)."""
        length = len(url or "")
        triggered = length > 80
        severity = "HIGH" if length > 120 else ("MEDIUM" if length > 80 else "LOW")
        score = 25 if length > 120 else (15 if length > 80 else 0)

        return {
            "indicator": "UNUSUAL_URL_LENGTH",
            "name": "URL Character Length",
            "triggered": triggered,
            "severity": severity,
            "score_contribution": score,
            "explanation": f"URL length is unusually long ({length} characters), typical of obfuscated phishing tokens." if triggered else f"URL length is normal ({length} characters).",
            "evidence": f"Total length: {length} chars" if triggered else None
        }

    def check_excessive_special_chars(self, url: str) -> Dict[str, Any]:
        """Indicator 7: Excessive Special Characters (-, _, =, %, ?, @)."""
        specials = sum(1 for c in url if c in "-_=%?@~&")
        triggered = specials >= 7
        severity = "HIGH" if specials >= 12 else ("MEDIUM" if specials >= 7 else "LOW")
        score = 20 if specials >= 12 else (12 if specials >= 7 else 0)

        return {
            "indicator": "EXCESSIVE_SPECIAL_CHARS",
            "name": "Special Character Density",
            "triggered": triggered,
            "severity": severity,
            "score_contribution": score,
            "explanation": f"High density of special symbols ({specials} characters) in URL structure." if triggered else "Standard symbol density.",
            "evidence": f"{specials} special characters" if triggered else None
        }

    def check_suspicious_encoding(self, url: str) -> Dict[str, Any]:
        """Indicator 8: Suspicious Hex / Double Percent Encoding."""
        has_double_encoding = "%25" in url.lower()
        has_hex_dots = "%2e" in url.lower() or "%2f" in url.lower()
        triggered = has_double_encoding or has_hex_dots

        return {
            "indicator": "SUSPICIOUS_ENCODING",
            "name": "Obfuscated / Double Encoding",
            "triggered": triggered,
            "severity": "HIGH" if triggered else "LOW",
            "score_contribution": 25 if triggered else 0,
            "explanation": "URL uses double percent-encoding or hex-encoded path separators to evade security filters." if triggered else "No obfuscated character encoding detected.",
            "evidence": "Hex obfuscation patterns (%25 / %2e / %2f)" if triggered else None
        }

    def check_suspicious_port(self, port: Optional[int]) -> Dict[str, Any]:
        """Indicator 9: Suspicious / Non-standard Web Port."""
        triggered = port is not None and port in NON_STANDARD_WEB_PORTS
        return {
            "indicator": "SUSPICIOUS_PORT",
            "name": "Non-Standard Network Port",
            "triggered": triggered,
            "severity": "HIGH" if triggered else "LOW",
            "score_contribution": 20 if triggered else 0,
            "explanation": f"URL connects over non-standard port :{port}, commonly used for rogue web servers." if triggered else "Uses standard web ports (80 / 443).",
            "evidence": f"Port :{port}" if triggered else None
        }

    def check_punycode_idn(self, hostname: str) -> Dict[str, Any]:
        """Indicator 10: Punycode / IDN Homograph Detection."""
        host = (hostname or "").lower()
        has_punycode = "xn--" in host
        return {
            "indicator": "PUNYCODE_IDN",
            "name": "Punycode Homograph Domain",
            "triggered": has_punycode,
            "severity": "HIGH" if has_punycode else "LOW",
            "score_contribution": 30 if has_punycode else 0,
            "explanation": "Domain uses Punycode (xn--) internationalized formatting, which can visually spoof trusted brands with Cyrillic/Greek characters." if has_punycode else "Standard ASCII domain name.",
            "evidence": host if has_punycode else None
        }

    def check_suspicious_keywords(self, url: str) -> Dict[str, Any]:
        """Indicator 11: Credential-Harvesting Keywords in Path/Query."""
        lower = url.lower()
        matched = [kw for kw in SUSPICIOUS_PATH_KEYWORDS if kw in lower]
        triggered = len(matched) >= 2
        severity = "HIGH" if len(matched) >= 3 else ("MEDIUM" if len(matched) >= 2 else "LOW")
        score = 25 if len(matched) >= 3 else (15 if len(matched) >= 2 else 0)

        return {
            "indicator": "SUSPICIOUS_KEYWORDS",
            "name": "Credential Harvesting Keywords",
            "triggered": triggered,
            "severity": severity,
            "score_contribution": score,
            "explanation": f"URL contains sensitive credential-harvesting keywords: {', '.join(matched[:4])}" if triggered else "No abnormal credential-harvesting keyword density.",
            "evidence": ", ".join(matched) if triggered else None
        }

    def check_lookalike_typosquatting(self, hostname: str) -> Dict[str, Any]:
        """
        Indicator 12: Brand Look-alike & Typosquatting Detection.
        Compares base domain against top targets using Levenshtein distance & character substitution maps.
        """
        if not hostname:
            return {
                "indicator": "LOOKALIKE_TYPOSQUATTING",
                "name": "Brand Typosquatting / Look-alike",
                "triggered": False,
                "severity": "HIGH",
                "score_contribution": 0,
                "explanation": "No brand impersonation detected.",
                "evidence": None
            }

        host_clean = hostname.lower().split(":")[0].strip("[]")
        base_domain = extract_base_domain(host_clean)
        domain_name_part = base_domain.split(".")[0] if "." in base_domain else base_domain

        # Normalize common 1337-speak substitutions
        normalized_part = (
            domain_name_part
            .replace("0", "o")
            .replace("1", "l")
            .replace("3", "e")
            .replace("5", "s")
            .replace("vv", "w")
            .replace("rn", "m")
        )

        matched_brand = None
        min_dist = 999
        explanation_msg = ""
        evidence_str = None

        for brand in TARGET_BRANDS:
            brand_name = brand["name"]
            for legitimate_domain in brand["domains"]:
                legit_base = extract_base_domain(legitimate_domain)
                legit_part = legit_base.split(".")[0]

                # Exact match with legitimate domain is SAFE (not typosquatting)
                if host_clean == legitimate_domain or host_clean.endswith(f".{legitimate_domain}"):
                    matched_brand = None
                    min_dist = 999
                    break

                # 1. Check if legit brand name appears inside a suspicious combo domain (e.g. paypal-security.com or paypa1-verify.com)
                if len(legit_part) >= 4 and (legit_part in domain_name_part or legit_part in normalized_part) and domain_name_part != legit_part:
                    matched_brand = brand_name
                    min_dist = 1
                    explanation_msg = f"This domain combines legitimate brand '{brand_name}' with extra deceptive keywords ({base_domain})."
                    evidence_str = f"Resembles {legitimate_domain} (contains '{legit_part}')"
                    break

                # 2. Levenshtein edit distance check on domain part
                dist = levenshtein_distance(domain_name_part, legit_part)
                norm_dist = levenshtein_distance(normalized_part, legit_part)

                # Homoglyph substitution (e.g. paypa1 -> paypal, g00gle -> google)
                is_homoglyph = (normalized_part == legit_part and domain_name_part != legit_part)
                
                if (is_homoglyph or dist in (1, 2) or (norm_dist in (1, 2) and norm_dist < dist)) and len(legit_part) >= 4:
                    effective_dist = 1 if is_homoglyph else min(dist, norm_dist)
                    if effective_dist < min_dist:
                        min_dist = effective_dist
                        matched_brand = brand_name
                        explanation_msg = f"This domain closely resembles '{brand_name}' ({legitimate_domain}) with an edit distance of {effective_dist}."
                        evidence_str = f"'{base_domain}' resembles legitimate '{legitimate_domain}'"

            if matched_brand and min_dist == 1:
                break

        triggered = matched_brand is not None

        return {
            "indicator": "LOOKALIKE_TYPOSQUATTING",
            "name": "Brand Typosquatting / Look-alike",
            "triggered": triggered,
            "severity": "HIGH" if triggered else "LOW",
            "score_contribution": 35 if triggered else 0,
            "explanation": explanation_msg if triggered else "No brand impersonation or typosquatting detected.",
            "evidence": evidence_str
        }

    def evaluate_all(self, url: str, parsed_content: Any) -> List[Dict[str, Any]]:
        """
        Runs all 12 heuristic checks on the provided URL and parsed content.
        Returns a complete list of structured indicator results.
        """
        scheme = parsed_content.scheme or ""
        hostname = parsed_content.hostname or ""
        port = parsed_content.port

        indicators = [
            self.check_https(scheme),
            self.check_ip_address_host(hostname),
            self.check_url_shortener(hostname),
            self.check_userinfo_trick(url),
            self.check_excessive_subdomains(hostname),
            self.check_unusual_length(url),
            self.check_excessive_special_chars(url),
            self.check_suspicious_encoding(url),
            self.check_suspicious_port(port),
            self.check_punycode_idn(hostname),
            self.check_suspicious_keywords(url),
            self.check_lookalike_typosquatting(hostname),
        ]

        return indicators


heuristic_engine = HeuristicEngine()
