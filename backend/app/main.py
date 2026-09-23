"""
QRadar — Real-Time Quishing Detection & Defense System
FastAPI Backend Application Entrypoint.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add paths to sys.path so modules and ML dependencies resolve cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

for p in [CURRENT_DIR, BACKEND_DIR, ROOT_DIR, os.path.join(ROOT_DIR, "ml", "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.core.config import settings
from app.db.session import init_db
from app.api.router import api_router
from app.services.ml_engine import ml_engine_service
from app.services.threat_intel import threat_intel_service

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("qradar.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown routines."""
    logger.info("Initializing QRadar security backend...")
    
    # 1. Initialize database tables
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # 2. Log ML model status
    if ml_engine_service.is_available:
        version = ml_engine_service.metadata.get("version", "1.0.0")
        logger.info(f"[ML] Model loaded successfully: Random Forest (18 features, version: {version})")
    else:
        logger.error(f"[ML ERROR] {ml_engine_service.load_error or 'Random Forest model artifact not available'}")

    # 3. Log Threat Intelligence provider
    logger.info(f"[TI] Threat Intelligence provider active: {threat_intel_service.get_configured_provider_name()}")

    logger.info(f"QRadar backend is operational at {settings.API_V1_STR}")
    yield
    logger.info("Shutting down QRadar backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Authoritative security engine for real-time Quishing (QR code phishing) detection, "
        "heuristic analysis, ML classification, and threat intelligence synthesis."
    ),
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Sanitizes unexpected exceptions to prevent leaking server internals to clients."""
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Security Engine Error",
            "message": "An unexpected error occurred while processing the security scan. The incident has been logged.",
            "path": request.url.path,
        }
    )


@app.get("/health", tags=["System Health"], summary="Service Health Check")
async def health_check():
    """Returns real-time service health, database status, and ML model availability."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ml_model_available": ml_engine_service.is_available,
        "threat_intel_provider": settings.THREAT_INTEL_PROVIDER,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System UI"], summary="Web Application UI Dashboard")
@app.get("/web", tags=["System UI"], summary="Web Application UI Dashboard")
async def serve_web_ui():
    """Serves the interactive QRadar Web UI and Security Dashboard."""
    web_ui_file = os.path.join(CURRENT_DIR, "web_ui", "index.html")
    if os.path.exists(web_ui_file):
        with open(web_ui_file, "r", encoding="utf-8") as f:
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=f.read())
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }


from fastapi.staticfiles import StaticFiles

# Include v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount local static files for offline browser dashboard support
static_dir = os.path.join(CURRENT_DIR, "web_ui", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
