"""
Dashboard Analytics API Endpoints.
Aggregates risk score distributions, threat counts, timelines, and top domains.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.dashboard import DashboardStats
from app.services.scan_service import scan_service

router = APIRouter(prefix="/dashboard", tags=["Security Dashboard & Analytics"])


@router.get(
    "",
    response_model=DashboardStats,
    summary="Get Security Dashboard Analytics",
    description="Retrieves aggregate metrics including safe/suspicious/malicious breakdown, risk distributions, timelines, and top domains."
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db)
):
    return await scan_service.get_dashboard_metrics(db=db)
