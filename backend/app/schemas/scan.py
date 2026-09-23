"""
Pydantic Schemas for Scan Requests, Decoded Payloads, and Security Evaluation Responses.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class URLScanRequest(BaseModel):
    url: str = Field(..., description="The URL or raw QR content string to analyze", min_length=1, max_length=4096)
    source: Optional[str] = Field("manual", description="Source of the scan: 'camera', 'gallery', or 'manual'")


class QRItem(BaseModel):
    content: str = Field(..., description="The raw decoded string content of the QR code")
    qr_type: str = Field(..., description="'url', 'text', 'upi', or 'dangerous_scheme'")
    polygon: Optional[List[List[float]]] = Field(None, description="Bounding polygon points if detected")


class MultiQRDecodeResponse(BaseModel):
    total_found: int = Field(..., description="Total number of QR codes detected in the image")
    qr_codes: List[QRItem] = Field(..., description="List of decoded QR codes")


class HeuristicIndicator(BaseModel):
    indicator: str = Field(..., description="Identifier name of the heuristic indicator")
    name: str = Field(..., description="Human-friendly name of the check")
    triggered: bool = Field(..., description="True if the heuristic check triggered suspicious risk")
    severity: str = Field(..., description="'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'")
    score_contribution: int = Field(..., description="Numerical risk points contributed by this indicator")
    explanation: str = Field(..., description="Explainable description of what was detected")
    evidence: Optional[str] = Field(None, description="Extracted evidence or snippet safely formatted")


class MLResult(BaseModel):
    available: bool = Field(..., description="Whether the ML inference model was available and executed")
    status: str = Field("ANALYZED", description="'ANALYZED', 'UNAVAILABLE', or 'NOT_APPLICABLE'")
    model_name: str = Field("Random Forest", description="Name of the machine learning model")
    prediction: Optional[str] = Field(None, description="'Phishing', 'Legitimate', or None")
    confidence: Optional[float] = Field(None, description="Prediction confidence |p - 0.5| * 2 (0.0 - 1.0)")
    uncertainty: Optional[float] = Field(None, description="Prediction uncertainty 1 - confidence (0.0 - 1.0)")
    phishing_probability: Optional[float] = Field(None, description="Calculated phishing risk probability (0.0 - 1.0)")
    model_version: Optional[str] = Field(None, description="Version of the ML model used")
    reason: Optional[str] = Field(None, description="Detailed explanatory reason if unavailable or not applicable")


class ThreatIntelResult(BaseModel):
    status: str = Field(..., description="'MALICIOUS', 'CLEAN', 'NOT_AVAILABLE', 'NOT_APPLICABLE' (or legacy aliases 'THREAT_FOUND', 'SUSPICIOUS', 'NO_THREAT_FOUND', 'NO_RECORD', 'UNAVAILABLE', 'NOT_CONFIGURED')")
    provider: str = Field(..., description="Name of the threat intelligence provider evaluated")
    checked: bool = Field(False, description="Whether the provider was actually queried")
    result: Optional[str] = Field(None, description="Standard result classification")
    message: Optional[str] = Field(None, description="Human readable message explaining threat intel findings")
    details: Optional[str] = Field(None, description="Detailed explanatory context or threat categorization")
    reason: Optional[str] = Field(None, description="Detailed explanatory reason if unavailable or not applicable")
    error_reason: Optional[str] = Field(None, description="Specific error category if failed, unconfigured, or unavailable")
    malicious_count: Optional[int] = Field(None, description="Count of engines flagging malicious")
    suspicious_count: Optional[int] = Field(None, description="Count of engines flagging suspicious")
    harmless_count: Optional[int] = Field(None, description="Count of engines flagging harmless")
    undetected_count: Optional[int] = Field(None, description="Count of engines flagging undetected")
    cached: bool = Field(False, description="Whether this lookup was served from local TTL cache")


class SecurityResult(BaseModel):
    scan_id: str = Field(..., description="Unique UUID identifier for this security evaluation")
    analyzed_at: str = Field(..., description="ISO 8601 UTC timestamp of analysis")
    
    # Content parsing
    content_type: str = Field(..., description="'url', 'text', 'upi', or 'dangerous_scheme'")
    original_content: str = Field(..., description="The original unmodified content extracted from the QR code")
    normalized_url: Optional[str] = Field(None, description="Safely normalized URL if applicable")
    domain: Optional[str] = Field(None, description="Domain/hostname parsed from the URL")
    scheme: Optional[str] = Field(None, description="URL protocol scheme (e.g., https, http, upi)")

    # Authoritative Verdict & Action
    verdict: str = Field(..., description="'SAFE', 'SUSPICIOUS', or 'MALICIOUS'")
    risk_score: int = Field(..., ge=0, le=100, description="Unified risk score from 0 (safest) to 100 (highest risk)")
    recommended_action: str = Field(..., description="'ALLOW', 'WARN', or 'BLOCK'")
    reasons: List[str] = Field(..., description="List of primary human-readable reasons explaining the verdict")

    # Deep breakdown
    heuristics: List[HeuristicIndicator] = Field(..., description="Detailed breakdown of all 12+ heuristic indicators")
    ml: MLResult = Field(..., description="Machine learning phishing classifier results")
    threat_intelligence: ThreatIntelResult = Field(..., description="External threat intelligence status")
    is_degraded: bool = Field(False, description="True if any external service or model operated in fallback mode")


class ScanHistoryItem(BaseModel):
    scan_id: str
    created_at: str
    content_type: str
    original_content: str
    normalized_url: Optional[str] = None
    domain: Optional[str] = None
    verdict: str
    risk_score: int
    recommended_action: str
    reasons: List[str]
    threat_intel_status: str
    ml_probability: Optional[float] = None
