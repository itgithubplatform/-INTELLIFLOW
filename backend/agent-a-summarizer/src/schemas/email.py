"""
Email Schemas
=============

Pydantic models for email-related requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EmailMetadata(BaseModel):
    """Email metadata from Gmail."""
    
    id: str = Field(description="Gmail message ID")
    thread_id: Optional[str] = Field(default=None, description="Gmail thread ID")
    subject: Optional[str] = Field(default=None)
    sender: Optional[str] = Field(default=None, description="Sender email address")
    sender_name: Optional[str] = Field(default=None)
    received_at: Optional[datetime] = Field(default=None)
    snippet: Optional[str] = Field(default=None, description="Email preview snippet")
    is_unread: bool = Field(default=True)
    is_important: bool = Field(default=False)
    labels: list[str] = Field(default_factory=list)


class EmailListRequest(BaseModel):
    """Request parameters for listing emails."""
    
    max_results: int = Field(default=20, ge=1, le=100)
    page_token: Optional[str] = Field(default=None)
    query: Optional[str] = Field(
        default=None,
        description="Gmail search query (e.g., 'is:unread after:2024/01/01')"
    )
    include_spam_trash: bool = Field(default=False)


class EmailListResponse(BaseModel):
    """Response containing list of emails."""
    
    emails: list[EmailMetadata] = Field(default_factory=list)
    next_page_token: Optional[str] = Field(default=None)
    total_count: int = Field(default=0)


class ActionItem(BaseModel):
    """Extracted action item from email."""
    
    title: str = Field(description="Action item description")
    deadline: Optional[str] = Field(default=None, description="Due date if mentioned")
    priority: str = Field(default="medium", description="low, medium, high, urgent")
    assignee: Optional[str] = Field(default=None, description="Person responsible")


class DetectedEvent(BaseModel):
    """Calendar event detected from email content."""
    
    title: str = Field(description="Event title")
    description: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None, description="Event date (YYYY-MM-DD)")
    time: Optional[str] = Field(default=None, description="Event time (HH:MM)")
    duration_minutes: int = Field(default=60)
    location: Optional[str] = Field(default=None)
    attendees: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class SummaryResult(BaseModel):
    """Result of summarizing a single email."""
    
    email_id: str
    success: bool
    summary: Optional[str] = Field(default=None)
    key_points: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    detected_events: list[DetectedEvent] = Field(default_factory=list)
    sentiment: Optional[str] = Field(default=None, description="positive, negative, neutral")
    priority: Optional[str] = Field(default=None, description="low, medium, high, urgent")
    error: Optional[str] = Field(default=None)


class SummarizeRequest(BaseModel):
    """Request to summarize emails."""
    
    email_ids: list[str] = Field(
        description="List of Gmail message IDs to summarize"
    )
    include_action_items: bool = Field(default=True)
    detect_calendar_events: bool = Field(default=True)
    create_calendar_events: bool = Field(
        default=False,
        description="If true, delegate to Agent B to create calendar events"
    )


class SummarizeResponse(BaseModel):
    """Response from email summarization."""
    
    success: bool
    results: list[SummaryResult] = Field(default_factory=list)
    calendar_events_created: list[dict] = Field(default_factory=list)
    total_processed: int
    successful_count: int
