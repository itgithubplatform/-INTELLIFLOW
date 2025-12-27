"""
Agent B API Routes
==================

FastAPI router combining all API endpoints.
"""

from fastapi import APIRouter

from .routes.health import router as health_router
from .routes.calendar import router as calendar_router

router = APIRouter()

# Include all route modules
router.include_router(health_router, tags=["Health"])
router.include_router(calendar_router, prefix="/calendar", tags=["Calendar"])
