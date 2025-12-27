"""
Calendar Schemas
================

Pydantic models for calendar-related requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AttendeeSchema(BaseModel):
    """Calendar event attendee."""
    
    email: str
    name: Optional[str] = None
    response_status: str = Field(
        default="needsAction",
        description="accepted, declined, tentative, needsAction"
    )


class CalendarEventCreate(BaseModel):
    """Request to create a calendar event."""
    
    title: str = Field(description="Event title")
    description: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    
    start_time: datetime = Field(description="Event start time (ISO format)")
    end_time: datetime = Field(description="Event end time (ISO format)")
    timezone: str = Field(default="UTC")
    is_all_day: bool = Field(default=False)
    
    attendees: list[AttendeeSchema] = Field(default_factory=list)
    
    # Optional: Source information (for events created from emails)
    source_email_id: Optional[str] = Field(default=None)
    source_summary_id: Optional[int] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Q1 Planning Meeting",
                "description": "Quarterly planning session for the team",
                "location": "Conference Room A",
                "start_time": "2024-01-15T14:00:00Z",
                "end_time": "2024-01-15T15:00:00Z",
                "timezone": "America/New_York",
                "attendees": [
                    {"email": "team@company.com", "name": "Team"}
                ]
            }
        }


class CalendarEventUpdate(BaseModel):
    """Request to update a calendar event."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: Optional[str] = None
    is_all_day: Optional[bool] = None
    
    attendees: Optional[list[AttendeeSchema]] = None


class CalendarEventResponse(BaseModel):
    """Response containing a calendar event."""
    
    id: str = Field(description="Event ID")
    google_event_id: Optional[str] = Field(default=None)
    
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    is_all_day: bool = False
    
    attendees: list[AttendeeSchema] = Field(default_factory=list)
    
    status: str = Field(default="confirmed")
    source: str = Field(default="user_created")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Sync info
    is_synced: bool = False
    last_synced_at: Optional[datetime] = None


class CalendarEventsListResponse(BaseModel):
    """Response containing list of calendar events."""
    
    events: list[CalendarEventResponse] = Field(default_factory=list)
    total_count: int = Field(default=0)
    next_page_token: Optional[str] = Field(default=None)
