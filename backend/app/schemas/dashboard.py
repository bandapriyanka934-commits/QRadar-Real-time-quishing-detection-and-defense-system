"""
Pydantic Schemas for Security Dashboard Statistics and Analytics.
"""

from typing import List, Dict
from pydantic import BaseModel, Field


class RiskDistribution(BaseModel):
    safe: int = Field(..., description="Count of scans with risk score 0 - 29")
    suspicious: int = Field(..., description="Count of scans with risk score 30 - 69")
    malicious: int = Field(..., description="Count of scans with risk score 70 - 100")


class VerdictCounts(BaseModel):
    safe: int
    suspicious: int
    malicious: int


class ThreatTimelinePoint(BaseModel):
    date: str = Field(..., description="Date formatted as YYYY-MM-DD")
    total: int
    safe: int
    suspicious: int
    malicious: int


class TopDomainItem(BaseModel):
    domain: str
    count: int
    highest_risk: int


class DashboardStats(BaseModel):
    total_scans: int = Field(..., description="Total lifetime scans processed")
    verdict_counts: VerdictCounts = Field(..., description="Breakdown of verdicts")
    risk_distribution: RiskDistribution = Field(..., description="Distribution across risk score brackets")
    average_risk_score: float = Field(..., description="Average risk score across all scans")
    blocked_threats_count: int = Field(..., description="Total scans where action was BLOCK")
    timeline: List[ThreatTimelinePoint] = Field(..., description="Chronological activity breakdown")
    top_scanned_domains: List[TopDomainItem] = Field(..., description="Most frequently inspected domains")
