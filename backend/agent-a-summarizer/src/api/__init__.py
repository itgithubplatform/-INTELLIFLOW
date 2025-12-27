"""
Agent A API Routes
==================

FastAPI router combining all API endpoints.
"""

from fastapi import APIRouter

from .routes.health import router as health_router
from .routes.summarize import router as summarize_router

router = APIRouter()

# Include all route modules
router.include_router(health_router, tags=["Health"])
router.include_router(summarize_router, prefix="/emails", tags=["Email Summarization"])
