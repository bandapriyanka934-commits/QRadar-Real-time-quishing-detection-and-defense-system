"""
History API Endpoints.
Retrieval and management of past scan logs.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.scan import ScanHistoryItem, SecurityResult
from app.services.scan_service import scan_service

router = APIRouter(prefix="/scans", tags=["Scan History"])


@router.get(
    "",
    response_model=List[ScanHistoryItem],
    summary="List Scan History",
    description="Retrieves a paginated list of previous scans, optionally filtered by verdict."
)
async def list_scans(
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    verdict: Optional[str] = Query(None, description="Filter by verdict: 'SAFE', 'SUSPICIOUS', or 'MALICIOUS'"),
    db: AsyncSession = Depends(get_db)
):
    return await scan_service.get_history(db=db, limit=limit, offset=offset, verdict=verdict)


@router.get(
    "/{scan_id}",
    response_model=SecurityResult,
    summary="Get Scan Details by ID",
    description="Fetches full security evaluation result by its unique scan ID."
)
async def get_scan_details(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await scan_service.get_scan_by_id(db=db, scan_id=scan_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID '{scan_id}' not found."
        )
    return result


@router.delete(
    "/{scan_id}",
    summary="Delete Scan Record",
    description="Removes a specific scan record from the database."
)
async def delete_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    success = await scan_service.delete_scan(db=db, scan_id=scan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID '{scan_id}' not found."
        )
    return {"message": "Scan record deleted successfully.", "scan_id": scan_id}


@router.delete(
    "",
    summary="Clear All Scan History",
    description="Deletes all recorded scan logs from the local database."
)
async def clear_all_scans(
    db: AsyncSession = Depends(get_db)
):
    count = await scan_service.clear_all_history(db=db)
    return {"message": f"Cleared {count} scan records."}
