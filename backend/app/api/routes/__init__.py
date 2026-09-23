"""API routes package."""
from app.api.routes.scan import router as scan_router
from app.api.routes.history import router as history_router
from app.api.routes.dashboard import router as dashboard_router

__all__ = ["scan_router", "history_router", "dashboard_router"]
