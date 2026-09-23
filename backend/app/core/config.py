"""
Application Configuration and Environment Settings for QRadar.
Configures backend parameters, security weights, rate limiting, and threat intelligence.
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "QRadar — Quishing Detection & Defense System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database (SQLite with async support)
    DATABASE_URL: str = "sqlite+aiosqlite:///./qradar.db"
    SYNC_DATABASE_URL: str = "sqlite:///./qradar.db"

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]

    # ML Model Artifacts & Consistency
    ML_MODEL_PATH: str = os.path.join("ml", "models", "phishing_rf_model.joblib")
    ML_METADATA_PATH: str = os.path.join("ml", "models", "model_metadata.json")

    # Threat Intelligence Configuration
    THREAT_INTEL_PROVIDER: str = "mock"  # "mock" (local offline DB), "google", "virustotal"
    GSB_API_KEY: str = ""
    VIRUSTOTAL_API_KEY: str = ""
    THREAT_INTEL_TIMEOUT_SECONDS: float = 3.0
    THREAT_INTEL_CACHE_TTL_HOURS: int = 24  # Provider-specific cache TTL

    # Shortener Resolution Guard
    RESOLVE_SHORTENERS: bool = False  # Disabled by default for strict safety
    SHORTENER_TIMEOUT_SECONDS: float = 3.0
    SHORTENER_MAX_HOPS: int = 3

    # Data Retention & Privacy
    RETENTION_DAYS: int = 30  # Auto-purge records older than 30 days
    STRIP_SENSITIVE_QUERY_PARAMS: bool = True  # Strip credential parameters from non-malicious stored scans

    # Rate Limiting (Process-local in-memory bucket)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Risk Engine Boundary Thresholds
    RISK_SAFE_THRESHOLD: int = 29          # 0 – 29: SAFE -> ALLOW
    RISK_SUSPICIOUS_THRESHOLD: int = 69    # 30 – 69: SUSPICIOUS -> WARN
    RISK_MALICIOUS_THRESHOLD: int = 70     # 70 – 100: MALICIOUS -> BLOCK

    # Risk Scoring Formula Weights
    WEIGHT_HEURISTICS_MAX: int = 55        # Maximum contribution from 12 deterministic heuristics
    WEIGHT_ML_MAX: int = 35                # Maximum contribution from Random Forest ML classifier
    WEIGHT_TI_MALICIOUS_BASE: int = 88     # Baseline risk for confirmed malicious threat feed hits
    WEIGHT_TI_SUSPICIOUS: int = 25         # Risk addition for suspicious threat feed signals
    WEIGHT_TI_CLEAN_DISCOUNT: int = 8      # Moderate safety discount for verified clean high-reputation domains
    WEIGHT_PRIVATE_IP_BASE: int = 75       # Baseline risk for private IP / SSRF targets
    WEIGHT_DANGEROUS_SCHEME: int = 98      # Deterministic risk for dangerous URI schemes

    # Image Upload Constraints
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
