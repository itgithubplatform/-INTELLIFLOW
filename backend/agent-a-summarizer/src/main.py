"""
Agent A - Email Summarizer
==========================

FastAPI application entry point for the email summarization agent.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.database import init_async_db, close_db
from shared.utils import setup_logging, get_logger

from .api.routes import router as api_router
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
    logger.info("Starting Agent A - Email Summarizer")
    logger.info(f"Debug mode: {settings.app.debug}")
    
    # Initialize database
    await init_async_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent A")
    await close_db()
    logger.info("Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="Agent A - Email Summarizer",
    description="""
    AI-powered email summarization agent for IntelliFlow.
    
    ## Features
    - Fetch and summarize email threads
    - Extract action items and deadlines
    - Delegate calendar event creation to Agent B
    
    ## Authentication
    All endpoints require a valid Descope JWT token.
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

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "agent": "agent-a-summarizer",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with agent information."""
    return {
        "name": "Agent A - Email Summarizer",
        "description": "AI-powered email summarization agent",
        "version": "1.0.0",
        "docs": "/docs" if settings.app.debug else None,
    }
