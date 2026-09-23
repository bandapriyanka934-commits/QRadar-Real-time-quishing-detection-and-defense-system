"""
Central API Router aggregating all v1 endpoints.
"""

from fastapi import APIRouter
from app.api.routes.scan import router as scan_router
from app.api.routes.history import router as history_router
from app.api.routes.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(scan_router)
api_router.include_router(history_router)
api_router.include_router(dashboard_router)
