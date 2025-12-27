"""
Health Check Routes
===================

Health and status endpoints for Agent B.
"""

from fastapi import APIRouter

from shared.database import AsyncSessionLocal

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns the current health status of the agent and its dependencies.
    """
    health_status = {
        "status": "healthy",
        "agent": "agent-b-calendar",
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check database connection
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes.
    
    Returns 200 if the agent is ready to accept traffic.
    """
    return {"ready": True}
