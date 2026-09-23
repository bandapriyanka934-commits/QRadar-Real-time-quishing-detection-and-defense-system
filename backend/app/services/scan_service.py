"""
Scan Orchestration and Persistence Service.
Coordinates URL parsing, Heuristics, ML Inference, Threat Intel, Unified Risk Evaluation,
and database persistence with comprehensive structured logging.
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete

from app.models.scan_db import ScanRecord
from app.schemas.scan import SecurityResult, HeuristicIndicator, MLResult, ThreatIntelResult, ScanHistoryItem
from app.schemas.dashboard import DashboardStats, VerdictCounts, RiskDistribution, ThreatTimelinePoint, TopDomainItem
from app.services.url_analyzer import url_analyzer_service, ParsedContent
from app.services.heuristic_engine import heuristic_engine
from app.services.ml_engine import ml_engine_service
from app.services.threat_intel import threat_intel_service
from app.services.risk_engine import risk_engine

logger = logging.getLogger("qradar.scan_service")


class ScanService:
    async def analyze_and_persist(
        self,
        raw_content: str,
        db: Optional[AsyncSession] = None,
        source: str = "manual"
    ) -> SecurityResult:
        """
        Executes the full end-to-end security pipeline for any raw QR text or URL,
        persists the result to SQLite, and returns a validated SecurityResult.
        """
        scan_id = str(uuid.uuid4())
        analyzed_at = datetime.now(timezone.utc).isoformat()

        logger.info(f"[QR] Payload decoded: '{raw_content[:80]}' (len: {len(raw_content)}, source: {source})")

        # Step 1: Parse and Normalize Content
        parsed: ParsedContent = url_analyzer_service.parse_and_normalize(raw_content)
        if parsed.content_type == "url":
            logger.info(f"[URL] URL detected: {parsed.normalized_url} (domain: {parsed.domain}, scheme: {parsed.scheme})")
        else:
            logger.info(f"[QR] Non-web payload detected: content_type={parsed.content_type}, scheme={parsed.scheme}")

        # Step 2: Evaluate Heuristics (only for URLs)
        if parsed.content_type == "url":
            heuristics_raw = heuristic_engine.evaluate_all(parsed.normalized_url or raw_content, parsed)
            triggered_count = len([h for h in heuristics_raw if h.get("triggered")])
            logger.info(f"[HEURISTIC] Analysis completed: {triggered_count} / {len(heuristics_raw)} indicators triggered")
        else:
            heuristics_raw = []

        # Step 3: Run ML Inference
        if parsed.content_type == "url":
            ml_data = ml_engine_service.predict(parsed.normalized_url or raw_content)
        elif parsed.is_dangerous_scheme:
            ml_data = ml_engine_service.not_applicable(reason=f"Unsupported dangerous scheme ({parsed.scheme}:)")
        else:
            ml_data = ml_engine_service.not_applicable(reason="Non-web QR payload")

        # Step 4: Threat Intelligence Lookup
        if parsed.content_type == "url":
            threat_data = await threat_intel_service.check(parsed.normalized_url or raw_content)
            logger.info(f"[TI] Provider: {threat_data.get('provider')}, Status: {threat_data.get('status')}")
            logger.info(f"[TI] Lookup completed for '{parsed.domain}'")
        elif parsed.is_dangerous_scheme:
            threat_data = threat_intel_service.not_applicable(reason=f"Unsupported dangerous scheme ({parsed.scheme}:)")
        else:
            threat_data = threat_intel_service.not_applicable(reason="No web URL/domain to check")

        # Step 5: Unified Risk Engine Scoring
        risk_result = risk_engine.evaluate(
            parsed=parsed,
            heuristics=heuristics_raw,
            ml_result=ml_data,
            threat_intel=threat_data
        )
        logger.info(f"[RISK] Final score calculated: {risk_result['risk_score']}/100")
        logger.info(f"[RISK] Verdict: {risk_result['verdict']}, Action: {risk_result['recommended_action']}")

        # Format typed response models
        heuristics_typed = [HeuristicIndicator(**h) for h in heuristics_raw]
        ml_typed = MLResult(**ml_data)
        threat_typed = ThreatIntelResult(**threat_data)

        security_result = SecurityResult(
            scan_id=scan_id,
            analyzed_at=analyzed_at,
            content_type=parsed.content_type,
            original_content=parsed.original_content,
            normalized_url=parsed.normalized_url,
            domain=parsed.domain,
            scheme=parsed.scheme,
            verdict=risk_result["verdict"],
            risk_score=risk_result["risk_score"],
            recommended_action=risk_result["recommended_action"],
            reasons=risk_result["reasons"],
            heuristics=heuristics_typed,
            ml=ml_typed,
            threat_intelligence=threat_typed,
            is_degraded=risk_result["is_degraded"],
        )

        # Step 6: Persist in SQLite Database with Data Retention & Privacy Considerations
        if db is not None:
            # Privacy policy: strip sensitive credential query tokens from stored safe records
            if risk_result["verdict"] == "SAFE":
                persisted_content = url_analyzer_service.sanitize_stored_url(parsed.original_content) or parsed.original_content
                persisted_norm_url = url_analyzer_service.sanitize_stored_url(parsed.normalized_url)
            else:
                persisted_content = parsed.original_content
                persisted_norm_url = parsed.normalized_url

            db_record = ScanRecord(
                id=scan_id,
                created_at=datetime.now(timezone.utc),
                content_type=parsed.content_type,
                original_content=persisted_content,
                normalized_url=persisted_norm_url,
                domain=parsed.domain,
                scheme=parsed.scheme,
                verdict=risk_result["verdict"],
                risk_score=risk_result["risk_score"],
                recommended_action=risk_result["recommended_action"],
                reasons_json=json.dumps(risk_result["reasons"]),
                heuristics_json=json.dumps(heuristics_raw),
                ml_available=1 if ml_data.get("available") else 0,
                ml_probability=ml_data.get("phishing_probability"),
                threat_intel_status=threat_data.get("status", "NOT_APPLICABLE"),
                threat_intel_provider=threat_data.get("provider", "None"),
            )
            db.add(db_record)
            await db.commit()

        return security_result

    async def get_history(
        self,
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        verdict: Optional[str] = None
    ) -> List[ScanHistoryItem]:
        """Fetches paginated scan history items."""
        query = select(ScanRecord).order_by(desc(ScanRecord.created_at)).offset(offset).limit(limit)
        if verdict:
            query = query.where(ScanRecord.verdict == verdict.upper())

        result = await db.execute(query)
        records = result.scalars().all()

        history_items = []
        for r in records:
            history_items.append(ScanHistoryItem(
                scan_id=r.id,
                created_at=r.created_at.isoformat() if r.created_at else "",
                content_type=r.content_type,
                original_content=r.original_content,
                normalized_url=r.normalized_url,
                domain=r.domain,
                verdict=r.verdict,
                risk_score=r.risk_score,
                recommended_action=r.recommended_action,
                reasons=r.reasons,
                threat_intel_status=r.threat_intel_status,
                ml_probability=r.ml_probability,
            ))
        return history_items

    async def get_scan_by_id(self, db: AsyncSession, scan_id: str) -> Optional[SecurityResult]:
        """Retrieves complete security evaluation by scan_id from database."""
        result = await db.execute(select(ScanRecord).where(ScanRecord.id == scan_id))
        r = result.scalar_one_or_none()
        if not r:
            return None

        heuristics_data = r.heuristics
        heuristics_typed = [HeuristicIndicator(**h) for h in heuristics_data]
        ml_typed = MLResult(
            available=bool(r.ml_available),
            status="ANALYZED" if r.ml_available else "NOT_APPLICABLE",
            model_name="Random Forest",
            prediction="Phishing" if (r.ml_probability and r.ml_probability >= 0.5) else ("Legitimate" if r.ml_available else None),
            confidence=r.ml_probability if (r.ml_probability and r.ml_probability >= 0.5) else ((1.0 - r.ml_probability) if r.ml_probability is not None else None),
            phishing_probability=r.ml_probability,
            model_version="1.0.0",
        )
        threat_typed = ThreatIntelResult(
            status=r.threat_intel_status,
            provider=r.threat_intel_provider,
            checked=r.threat_intel_status in {"THREAT_FOUND", "SUSPICIOUS", "NO_THREAT_FOUND", "NO_RECORD", "CLEAN"},
            result=r.threat_intel_status,
            message=None,
            details=None,
            cached=False,
        )

        return SecurityResult(
            scan_id=r.id,
            analyzed_at=r.created_at.isoformat() if r.created_at else "",
            content_type=r.content_type,
            original_content=r.original_content,
            normalized_url=r.normalized_url,
            domain=r.domain,
            scheme=r.scheme,
            verdict=r.verdict,
            risk_score=r.risk_score,
            recommended_action=r.recommended_action,
            reasons=r.reasons,
            heuristics=heuristics_typed,
            ml=ml_typed,
            threat_intelligence=threat_typed,
            is_degraded=False,
        )

    async def delete_scan(self, db: AsyncSession, scan_id: str) -> bool:
        """Deletes a single scan by ID."""
        result = await db.execute(select(ScanRecord).where(ScanRecord.id == scan_id))
        record = result.scalar_one_or_none()
        if not record:
            return False
        await db.delete(record)
        await db.commit()
        return True

    async def purge_expired_records(self, db: AsyncSession) -> int:
        """Purges scan records older than the configured RETENTION_DAYS."""
        from datetime import timedelta
        from app.core.config import settings
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.RETENTION_DAYS)
        res = await db.execute(delete(ScanRecord).where(ScanRecord.created_at < cutoff))
        await db.commit()
        purged_count = res.rowcount or 0
        if purged_count > 0:
            logger.info(f"[DATA RETENTION] Purged {purged_count} scan records older than {settings.RETENTION_DAYS} days.")
        return purged_count

    async def clear_all_history(self, db: AsyncSession) -> int:
        """Clears all scan history records."""
        res = await db.execute(delete(ScanRecord))
        await db.commit()
        return res.rowcount or 0

    async def get_dashboard_metrics(self, db: AsyncSession) -> DashboardStats:
        """Aggregates real-time stats, risk distributions, and timelines for the dashboard."""
        all_scans_res = await db.execute(select(ScanRecord).order_by(desc(ScanRecord.created_at)))
        records = all_scans_res.scalars().all()

        total_scans = len(records)
        safe_count = 0
        suspicious_count = 0
        malicious_count = 0
        dist_safe = 0
        dist_suspicious = 0
        dist_malicious = 0
        total_risk = 0
        blocked_count = 0

        timeline_map: Dict[str, Dict[str, int]] = {}
        domain_map: Dict[str, Dict[str, int]] = {}

        for r in records:
            # Verdict counts
            v = (r.verdict or "SAFE").upper()
            if v == "SAFE":
                safe_count += 1
            elif v == "SUSPICIOUS":
                suspicious_count += 1
            else:
                malicious_count += 1

            # Risk score distribution
            score = r.risk_score or 0
            total_risk += score
            if score < 30:
                dist_safe += 1
            elif score < 70:
                dist_suspicious += 1
            else:
                dist_malicious += 1

            if (r.recommended_action or "").upper() == "BLOCK":
                blocked_count += 1

            # Timeline aggregation by date
            date_str = r.created_at.strftime("%Y-%m-%d") if r.created_at else "Today"
            if date_str not in timeline_map:
                timeline_map[date_str] = {"total": 0, "safe": 0, "suspicious": 0, "malicious": 0}
            timeline_map[date_str]["total"] += 1
            if v == "SAFE":
                timeline_map[date_str]["safe"] += 1
            elif v == "SUSPICIOUS":
                timeline_map[date_str]["suspicious"] += 1
            else:
                timeline_map[date_str]["malicious"] += 1

            # Top domains
            dom = r.domain or ("UPI Payment" if r.content_type == "upi" else "Text Content")
            if dom not in domain_map:
                domain_map[dom] = {"count": 0, "highest_risk": 0}
            domain_map[dom]["count"] += 1
            domain_map[dom]["highest_risk"] = max(domain_map[dom]["highest_risk"], score)

        avg_risk = round(total_risk / total_scans, 1) if total_scans > 0 else 0.0

        timeline_points = [
            ThreatTimelinePoint(
                date=k,
                total=v["total"],
                safe=v["safe"],
                suspicious=v["suspicious"],
                malicious=v["malicious"]
            )
            for k, v in sorted(timeline_map.items())
        ]

        top_domains = [
            TopDomainItem(domain=k, count=v["count"], highest_risk=v["highest_risk"])
            for k, v in sorted(domain_map.items(), key=lambda item: item[1]["count"], reverse=True)[:10]
        ]

        return DashboardStats(
            total_scans=total_scans,
            verdict_counts=VerdictCounts(
                safe=safe_count,
                suspicious=suspicious_count,
                malicious=malicious_count
            ),
            risk_distribution=RiskDistribution(
                safe=dist_safe,
                suspicious=dist_suspicious,
                malicious=dist_malicious
            ),
            average_risk_score=avg_risk,
            blocked_threats_count=blocked_count,
            timeline=timeline_points,
            top_scanned_domains=top_domains
        )


scan_service = ScanService()
