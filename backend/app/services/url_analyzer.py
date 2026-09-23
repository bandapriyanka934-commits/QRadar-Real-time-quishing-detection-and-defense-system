"""
URL Parsing, Scheme Validation, Safe Normalization, SSRF Guard, and Shortener Resolution Service.
Authoritatively validates and normalizes QR payloads without executing arbitrary network requests.
Supports standard HTTP/HTTPS URLs, UPI payment payloads, custom URI schemes, and dangerous execution schemes.
"""

import ipaddress
import socket
import re
from urllib.parse import urlparse, urlunparse, parse_qs, unquote
from typing import Dict, Any, Optional, Tuple, List
import httpx

from app.core.config import settings

# Dangerous URI schemes that can execute code, access local files, or trigger intents
DANGEROUS_SCHEMES = {
    "javascript",
    "data",
    "file",
    "blob",
    "intent",
    "about",
    "vbscript",
    "content",
    "chrome",
    "res",
    "mhtml",
    "jar",
    "ws",
    "wss",
}

# Regex to detect potential URLs without explicit scheme
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?$",
    re.IGNORECASE
)

# Regex to check if text is an IP address host with path
IP_HOST_REGEX = re.compile(
    r"^(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?$"
)

# Sensitive query keys to strip for privacy on stored non-malicious records
SENSITIVE_QUERY_KEYS = {
    "token", "auth", "session", "key", "password", "pwd", "secret", "access_token", "api_key", "bearer"
}


class ParsedContent:
    def __init__(
        self,
        content_type: str,
        original_content: str,
        normalized_url: Optional[str] = None,
        scheme: Optional[str] = None,
        domain: Optional[str] = None,
        hostname: Optional[str] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
        query: Optional[str] = None,
        is_private_ip: bool = False,
        is_dangerous_scheme: bool = False,
        danger_reason: Optional[str] = None,
        upi_params: Optional[Dict[str, str]] = None,
    ):
        self.content_type = content_type
        self.original_content = original_content
        self.normalized_url = normalized_url
        self.scheme = scheme
        self.domain = domain
        self.hostname = hostname
        self.port = port
        self.path = path
        self.query = query
        self.is_private_ip = is_private_ip
        self.is_dangerous_scheme = is_dangerous_scheme
        self.danger_reason = danger_reason
        self.upi_params = upi_params or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_type": self.content_type,
            "original_content": self.original_content,
            "normalized_url": self.normalized_url,
            "scheme": self.scheme,
            "domain": self.domain,
            "hostname": self.hostname,
            "port": self.port,
            "path": self.path,
            "query": self.query,
            "is_private_ip": self.is_private_ip,
            "is_dangerous_scheme": self.is_dangerous_scheme,
            "danger_reason": self.danger_reason,
            "upi_params": self.upi_params,
        }


class URLAnalyzerService:
    @staticmethod
    def is_private_or_loopback_ip(hostname: str) -> bool:
        """
        Checks if a given hostname or IP is a private, loopback, link-local, multicast,
        unspecified, reserved, or internal intranet address.
        """
        if not hostname:
            return False

        host_raw = hostname.strip().lower()
        if host_raw.startswith("[") and "]" in host_raw:
            host_clean = host_raw.split("]")[0].strip("[]")
        elif host_raw.count(":") > 1:
            # Raw IPv6 without brackets (e.g. ::1, fe80::1, ::ffff:127.0.0.1)
            host_clean = host_raw
        else:
            host_clean = host_raw.split(":")[0]

        if host_clean in {"localhost", "127.0.0.1", "::1", "0.0.0.0"} or host_clean.endswith(".localhost") or host_clean.endswith(".local") or host_clean.endswith(".internal"):
            return True

        try:
            ip_obj = ipaddress.ip_address(host_clean)
            # Handle IPv6-mapped IPv4 addresses (e.g. ::ffff:127.0.0.1)
            if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
                ip_obj = ip_obj.ipv4_mapped

            return (
                not ip_obj.is_global
                or ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_reserved
                or ip_obj.is_multicast
                or ip_obj.is_unspecified
            )
        except ValueError:
            return False

    @staticmethod
    def validate_outbound_url_ssrf(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validates outbound network requests against SSRF and DNS rebinding risks.
        Resolves DNS and blocks loopback, RFC 1918 private, link-local, multicast, and reserved addresses.
        """
        try:
            raw_url = (url or "").strip()
            parsed = urlparse(raw_url)
            # If no scheme was present at all
            if not parsed.scheme and not raw_url.startswith("//"):
                parsed = urlparse(f"http://{raw_url}")

            scheme = (parsed.scheme or "").lower()
            if scheme not in {"http", "https"}:
                return False, f"Unsupported outbound scheme '{scheme}:' (only http/https allowed)"

            hostname = (parsed.hostname or "").lower()
            if not hostname:
                return False, "Missing hostname in destination URL"

            # Check direct hostname/IP representation
            if URLAnalyzerService.is_private_or_loopback_ip(hostname):
                return False, f"Destination points to a blocked private/loopback IP address or local hostname ({hostname})"

            # Resolve DNS addresses safely
            try:
                addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
                if not addr_info:
                    return False, f"No DNS records returned for '{hostname}'"

                for family, socktype, proto, canonname, sockaddr in addr_info:
                    ip_str = sockaddr[0]
                    ip_obj = ipaddress.ip_address(ip_str)
                    if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
                        ip_obj = ip_obj.ipv4_mapped

                    if (
                        not ip_obj.is_global
                        or ip_obj.is_private
                        or ip_obj.is_loopback
                        or ip_obj.is_link_local
                        or ip_obj.is_reserved
                        or ip_obj.is_multicast
                        or ip_obj.is_unspecified
                    ):
                        return False, f"Domain '{hostname}' resolves to blocked private/internal address {ip_str}"
            except socket.gaierror as e:
                return False, f"DNS resolution failed for '{hostname}': {e}"

            return True, None
        except Exception as e:
            return False, f"URL SSRF validation error: {e}"

    async def resolve_shortener_safely(self, url: str) -> Dict[str, Any]:
        """
        Safely follows HTTP redirects with strict hop limits, DNS validation, and SSRF protection.
        Returns destination URL and hop history.
        """
        if not settings.RESOLVE_SHORTENERS:
            return {
                "status": "NOT_AVAILABLE",
                "resolved_url": url,
                "hops": 0,
                "reason": "Shortener resolution is disabled in configuration"
            }

        current_url = url
        hops: List[str] = [current_url]

        for hop_idx in range(settings.SHORTENER_MAX_HOPS):
            # Validate SSRF for current destination
            is_safe, reason = self.validate_outbound_url_ssrf(current_url)
            if not is_safe:
                return {
                    "status": "FAILED",
                    "resolved_url": current_url,
                    "hops": len(hops),
                    "reason": f"SSRF security guard blocked resolution: {reason}"
                }

            try:
                async with httpx.AsyncClient(
                    follow_redirects=False,
                    timeout=settings.SHORTENER_TIMEOUT_SECONDS
                ) as client:
                    resp = await client.head(current_url)
                    if resp.status_code in {301, 302, 303, 307, 308}:
                        redirect_target = resp.headers.get("Location")
                        if not redirect_target:
                            break
                        
                        # Prevent HTTPS to HTTP downgrade
                        if current_url.startswith("https://") and redirect_target.startswith("http://"):
                            return {
                                "status": "FAILED",
                                "resolved_url": current_url,
                                "hops": len(hops),
                                "reason": "HTTPS downgrade redirect prohibited"
                            }

                        current_url = redirect_target
                        hops.append(current_url)
                    else:
                        break
            except Exception as e:
                return {
                    "status": "NOT_AVAILABLE",
                    "resolved_url": current_url,
                    "hops": len(hops),
                    "reason": f"Network error during resolution: {str(e)}"
                }

        return {
            "status": "RESOLVED",
            "resolved_url": current_url,
            "hops": len(hops),
            "reason": None
        }

    @staticmethod
    def sanitize_stored_url(url: Optional[str]) -> Optional[str]:
        """
        Strips authentication tokens and passwords from stored query parameters on safe scans.
        Preserves path, domain, and non-sensitive query arguments.
        """
        if not url or not settings.STRIP_SENSITIVE_QUERY_PARAMS:
            return url
        try:
            parsed = urlparse(url)
            if not parsed.query:
                return url
            query_dict = parse_qs(parsed.query, keep_blank_values=True)
            sanitized_query = []
            for k, vals in query_dict.items():
                if k.lower() in SENSITIVE_QUERY_KEYS:
                    sanitized_query.append(f"{k}=[REDACTED]")
                else:
                    for v in vals:
                        sanitized_query.append(f"{k}={v}")
            new_query = "&".join(sanitized_query)
            return urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
        except Exception:
            return url

    def parse_and_normalize(self, raw_content: str) -> ParsedContent:
        """
        Parses raw QR content string into a structured, safely normalized representation.
        Explicitly identifies dangerous URI schemes, UPI payment payloads, plain text, and HTTP/HTTPS URLs.
        """
        raw = (raw_content or "").strip()
        if not raw:
            return ParsedContent(
                content_type="text",
                original_content="",
                normalized_url=None,
            )

        # 1. Check for dangerous URI schemes
        colon_idx = raw.find(":")
        if colon_idx != -1:
            scheme_candidate = raw[:colon_idx].strip().lower()
            if scheme_candidate in DANGEROUS_SCHEMES:
                return ParsedContent(
                    content_type="dangerous_scheme",
                    original_content=raw,
                    scheme=scheme_candidate,
                    is_dangerous_scheme=True,
                    danger_reason=(
                        f"Potentially malicious execution scheme '{scheme_candidate}:' detected. "
                        "Opening this scheme can trigger local code execution, arbitrary intents, or file exfiltration."
                    )
                )

        # 2. Check for UPI payment URI scheme (upi://pay?pa=... or upi:pay?pa=...)
        if colon_idx != -1:
            scheme_candidate = raw[:colon_idx].strip().lower()
            if scheme_candidate == "upi":
                query_str = ""
                if "?" in raw:
                    query_str = raw.split("?", 1)[1]
                params_raw = parse_qs(query_str)
                upi_params = {k: v[0] if v else "" for k, v in params_raw.items()}

                return ParsedContent(
                    content_type="upi",
                    original_content=raw,
                    scheme="upi",
                    domain=None,
                    hostname=None,
                    normalized_url=None,
                    upi_params=upi_params,
                    is_dangerous_scheme=False,
                )

        # 3. Determine if URL or Plain Text
        is_http_scheme = raw.lower().startswith("http://") or raw.lower().startswith("https://")
        is_implicit_url = DOMAIN_REGEX.match(raw) is not None or IP_HOST_REGEX.match(raw) is not None

        if not is_http_scheme and not is_implicit_url:
            if colon_idx != -1 and not raw.startswith("//"):
                custom_scheme = raw[:colon_idx].strip().lower()
                if custom_scheme in {"mailto", "tel", "sms", "smsto", "wifi", "geo", "facetime"}:
                    return ParsedContent(
                        content_type="text",
                        original_content=raw,
                        scheme=custom_scheme,
                        normalized_url=None,
                    )
            return ParsedContent(
                content_type="text",
                original_content=raw,
                normalized_url=None,
            )

        # 4. Normalize HTTP / HTTPS URL
        url_to_parse = raw if is_http_scheme else f"http://{raw}"
        try:
            parsed = urlparse(url_to_parse)
        except Exception:
            return ParsedContent(
                content_type="text",
                original_content=raw,
                normalized_url=None,
            )

        scheme = (parsed.scheme or "http").lower()
        netloc = parsed.netloc or ""
        hostname = (parsed.hostname or "").lower()
        port = parsed.port
        path = parsed.path or "/"
        query = parsed.query or ""
        fragment = parsed.fragment or ""

        # Normalize port
        port_str = ""
        if port:
            if (scheme == "http" and port != 80) or (scheme == "https" and port != 443):
                port_str = f":{port}"

        # Reconstruct clean netloc
        if parsed.username or parsed.password:
            user_part = f"{parsed.username or ''}{f':{parsed.password}' if parsed.password else ''}@"
        else:
            user_part = ""
        clean_netloc = f"{user_part}{hostname}{port_str}"

        # Normalize path
        normalized_path = path if path.startswith("/") else f"/{path}"

        # Reassemble normalized URL
        normalized_url = urlunparse((
            scheme,
            clean_netloc,
            normalized_path,
            parsed.params or "",
            query,
            fragment
        ))

        # Check for private IP / SSRF host
        is_private = self.is_private_or_loopback_ip(hostname)

        return ParsedContent(
            content_type="url",
            original_content=raw,
            normalized_url=normalized_url,
            scheme=scheme,
            domain=hostname,
            hostname=hostname,
            port=port,
            path=normalized_path,
            query=query,
            is_private_ip=is_private,
            is_dangerous_scheme=False
        )


url_analyzer_service = URLAnalyzerService()
