"""
Agent B - Calendar Manager
==========================

FastAPI application entry point for the calendar management agent.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.database import init_async_db, close_db
from shared.utils import setup_logging, get_logger

from .api.routes import router as api_router
from .api.middleware.auth_middleware import TokenValidationMiddleware
from .core.config import agent_settings

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Initializes resources on startup and cleans up on shutdown.
    """
    # Startup
    logger.info("Starting Agent B - Calendar Manager")
    logger.info(f"Debug mode: {settings.app.debug}")
    
    # Initialize database
    await init_async_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent B")
    await close_db()
    logger.info("Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="Agent B - Calendar Manager",
    description="""
    Calendar management agent for IntelliFlow.
    
    ## Features
    - Create, read, update, and delete calendar events
    - Sync with Google Calendar
    - Accept delegated tokens from Agent A
    
    ## Authentication
    All endpoints require a valid Descope JWT token with appropriate scopes.
    Delegated tokens from Agent A are accepted for calendar operations.
    
    ## Required Scopes
    - `calendar.read`: Read calendar events
    - `calendar.write`: Create/modify calendar events
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.app.debug else None,
    redoc_url="/redoc" if settings.app.debug else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add token validation middleware
app.add_middleware(TokenValidationMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "agent": "agent-b-calendar",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with agent information."""
    return {
        "name": "Agent B - Calendar Manager",
        "description": "Calendar management agent with Google Calendar integration",
        "version": "1.0.0",
        "docs": "/docs" if settings.app.debug else None,
        "required_scopes": ["calendar.read", "calendar.write"]
    }
