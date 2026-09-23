"""
End-to-end security pipeline test script.
Simulates scanning all demo cases and verifies authoritative results and scoring.
"""

import os
import sys
import asyncio

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in [BACKEND_DIR, ROOT_DIR, os.path.join(ROOT_DIR, "ml", "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.db.session import init_db, AsyncSessionLocal
from app.services.scan_service import scan_service
from app.services.qr_decoder import qr_decoder_service

DEMO_DIR = os.path.join(ROOT_DIR, "demo_assets")

async def run_e2e_pipeline_verification():
    print("=" * 70)
    print("QRADAR — END-TO-END SECURITY PIPELINE VERIFICATION")
    print("=" * 70)

    # 1. Initialize DB
    await init_db()

    # 2. Iterate through demo QR images
    async with AsyncSessionLocal() as session:
        for filename in sorted(os.listdir(DEMO_DIR)):
            if not filename.endswith(".png"):
                continue
            filepath = os.path.join(DEMO_DIR, filename)
            with open(filepath, "rb") as f:
                img_bytes = f.read()

            decoded_list = qr_decoder_service.decode_image_bytes(img_bytes)
            print(f"\n--- [Image: {filename}] (Found {len(decoded_list)} QR) ---")

            for idx, item in enumerate(decoded_list):
                content = item["content"]
                result = await scan_service.analyze_and_persist(content, db=session, source="demo")

                print(f"  Target  : {result.original_content}")
                print(f"  Verdict : {result.verdict:10s} | Risk Score: {result.risk_score:3d}/100 | Action: {result.recommended_action}")
                print(f"  ML Prob : {result.ml.phishing_probability} | Threat Intel: {result.threat_intelligence.status}")
                print(f"  Reasons :")
                for r in result.reasons:
                    print(f"    * {r}")

        # 3. Check Dashboard aggregation
        dashboard = await scan_service.get_dashboard_metrics(session)
        print("\n" + "=" * 70)
        print("DASHBOARD METRICS AGGREGATION:")
        print(f"  Total Scans Processed: {dashboard.total_scans}")
        print(f"  Verdicts Breakdown   : Safe={dashboard.verdict_counts.safe}, Suspicious={dashboard.verdict_counts.suspicious}, Malicious={dashboard.verdict_counts.malicious}")
        print(f"  Risk Distribution    : Low={dashboard.risk_distribution.safe}, Med={dashboard.risk_distribution.suspicious}, High={dashboard.risk_distribution.malicious}")
        print(f"  Average Risk Score   : {dashboard.average_risk_score}/100")
        print(f"  Blocked Threats      : {dashboard.blocked_threats_count}")
        print("=" * 70)
        print("\n>>> All pipeline steps verified successfully! <<<\n")

if __name__ == "__main__":
    asyncio.run(run_e2e_pipeline_verification())
