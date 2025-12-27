"""
Summary Schemas
===============

Additional Pydantic models for summarization operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SummaryMetrics(BaseModel):
    """Metrics about the summarization process."""
    
    tokens_used: int = Field(default=0)
    processing_time_ms: int = Field(default=0)
    model_used: str = Field(default="claude-3-sonnet")


class BatchSummarizeRequest(BaseModel):
    """Request for batch email summarization."""
    
    query: Optional[str] = Field(
        default="is:unread",
        description="Gmail search query to find emails"
    )
    max_emails: int = Field(default=10, ge=1, le=50)
    include_action_items: bool = Field(default=True)
    detect_calendar_events: bool = Field(default=True)
    create_calendar_events: bool = Field(default=False)
    async_processing: bool = Field(
        default=False,
        description="If true, process in background and return task ID"
    )


class BatchSummarizeResponse(BaseModel):
    """Response from batch summarization."""
    
    task_id: Optional[str] = Field(default=None, description="Celery task ID if async")
    status: str = Field(description="pending, processing, completed, failed")
    processed_count: int = Field(default=0)
    results: Optional[list] = Field(default=None)
    estimated_completion: Optional[datetime] = Field(default=None)


class TaskStatusResponse(BaseModel):
    """Response for checking task status."""
    
    task_id: str
    status: str = Field(description="pending, processing, completed, failed")
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    result: Optional[dict] = Field(default=None)
    error: Optional[str] = Field(default=None)
