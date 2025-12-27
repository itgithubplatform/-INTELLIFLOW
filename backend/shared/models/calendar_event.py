"""
Calendar Event Model
====================

Models for storing calendar events created by Agent B.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class EventSource(str, Enum):
    """Source of calendar event creation."""
    EMAIL_SUMMARY = "email_summary"
    USER_CREATED = "user_created"
    AGENT_SCHEDULED = "agent_scheduled"


class EventStatus(str, Enum):
    """Calendar event status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CalendarEvent(Base, TimestampMixin):
    """
    Calendar event model.
    
    Stores events created by Agent B from email summaries or user input.
    """
    
    __tablename__ = "calendar_events"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Google Calendar identifiers
    google_event_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    google_calendar_id: Mapped[str] = mapped_column(String(255), default="primary")
    
    # Event details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Timing
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")
    
    # Recurrence
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(Text)  # RRULE format
    
    # Attendees
    attendees: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    # Example: [{"email": "user@example.com", "name": "John", "response": "accepted"}]
    
    # Source tracking
    source: Mapped[str] = mapped_column(
        String(50),
        default=EventSource.EMAIL_SUMMARY.value
    )
    source_email_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("emails.id", ondelete="SET NULL")
    )
    source_summary_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("email_summaries.id", ondelete="SET NULL")
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default=EventStatus.PENDING.value
    )
    
    # Sync status
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sync_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # Reminders
    reminders: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    # Example: {"useDefault": false, "overrides": [{"method": "email", "minutes": 30}]}
    
    # Agent metadata
    confidence_score: Mapped[Optional[float]] = mapped_column()  # 0.0 to 1.0
    extraction_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Table indexes
    __table_args__ = (
        Index("idx_calendar_events_user_id", "user_id"),
        Index("idx_calendar_events_google_event_id", "google_event_id"),
        Index("idx_calendar_events_start_time", "start_time"),
        Index("idx_calendar_events_status", "status"),
        Index("idx_calendar_events_source", "source"),
    )
    
    def __repr__(self) -> str:
        return f"<CalendarEvent {self.title} at {self.start_time}>"
    
    @property
    def duration_minutes(self) -> int:
        """Calculate event duration in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
