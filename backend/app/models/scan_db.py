"""
SQLAlchemy ORM Models for persisting scan records and provider-specific Threat Intel TTL cache in SQLite.
"""

import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ScanRecord(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Content & Source
    content_type = Column(String(32), nullable=False)  # "url", "text", "upi", "dangerous_scheme"
    original_content = Column(Text, nullable=False)
    normalized_url = Column(Text, nullable=True)
    domain = Column(String(255), nullable=True, index=True)
    scheme = Column(String(32), nullable=True)

    # Security Verdict & Risk
    verdict = Column(String(32), nullable=False, index=True)  # "SAFE", "SUSPICIOUS", "MALICIOUS"
    risk_score = Column(Integer, nullable=False)              # 0 - 100
    recommended_action = Column(String(32), nullable=False)   # "ALLOW", "WARN", "BLOCK"
    reasons_json = Column(Text, nullable=False)               # JSON-serialized list of strings

    # Detailed signals
    heuristics_json = Column(Text, nullable=False)           # JSON-serialized list of indicator dicts
    ml_available = Column(Integer, default=1)                 # 1 or 0
    ml_probability = Column(Float, nullable=True)             # 0.0 - 1.0
    threat_intel_status = Column(String(64), nullable=False)  # "MALICIOUS", "CLEAN", "NOT_AVAILABLE", "NOT_APPLICABLE", etc.
    threat_intel_provider = Column(String(64), nullable=False)

    @property
    def reasons(self):
        try:
            return json.loads(self.reasons_json)
        except Exception:
            return []

    @property
    def heuristics(self):
        try:
            return json.loads(self.heuristics_json)
        except Exception:
            return []


class ThreatIntelCache(Base):
    """
    Provider-specific TTL cache for Threat Intelligence lookups.
    Key is conceptually (provider, url_hash).
    """
    __tablename__ = "threat_intel_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(64), nullable=False, index=True)
    url_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False)
    details = Column(Text, nullable=True)
    response_json = Column(Text, nullable=False)
    checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
