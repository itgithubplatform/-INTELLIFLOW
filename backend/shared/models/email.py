"""
Email Model
===========

Models for storing email data and AI-generated summaries.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class EmailStatus(str, Enum):
    """Email processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUMMARIZED = "summarized"
    FAILED = "failed"


class Email(Base, TimestampMixin):
    """
    Email model for storing fetched emails.
    
    Stores email metadata and content for summarization.
    """
    
    __tablename__ = "emails"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Gmail message identifiers
    gmail_id: Mapped[str] = mapped_column(String(255), nullable=False)
    thread_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Email metadata
    subject: Mapped[Optional[str]] = mapped_column(Text)
    sender: Mapped[Optional[str]] = mapped_column(String(255))
    sender_name: Mapped[Optional[str]] = mapped_column(String(255))
    recipients: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    
    # Content
    snippet: Mapped[Optional[str]] = mapped_column(Text)
    body_text: Mapped[Optional[str]] = mapped_column(Text)
    body_html: Mapped[Optional[str]] = mapped_column(Text)
    
    # Email dates
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Labels and categories
    labels: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    is_unread: Mapped[bool] = mapped_column(Boolean, default=True)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Processing status
    status: Mapped[str] = mapped_column(
        String(50),
        default=EmailStatus.PENDING.value
    )
    
    # Relationships
    summaries: Mapped[list["EmailSummary"]] = relationship(
        "EmailSummary",
        back_populates="email",
        cascade="all, delete-orphan"
    )
    
    # Table indexes
    __table_args__ = (
        Index("idx_emails_user_id", "user_id"),
        Index("idx_emails_gmail_id", "gmail_id"),
        Index("idx_emails_thread_id", "thread_id"),
        Index("idx_emails_received_at", "received_at"),
        Index("idx_emails_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Email {self.gmail_id}: {self.subject[:50] if self.subject else 'No Subject'}>"


class EmailSummary(Base, TimestampMixin):
    """
    AI-generated email summary.
    
    Stores the summary, extracted action items, and detected events.
    """
    
    __tablename__ = "email_summaries"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("emails.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Summary content
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    
    # Extracted action items
    action_items: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    # Example: [{"title": "Follow up", "deadline": "2024-01-15", "priority": "high"}]
    
    # Detected events/meetings
    detected_events: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    # Example: [{"title": "Meeting", "date": "2024-01-15", "time": "10:00", "attendees": [...]}]
    
    # Sentiment and priority
    sentiment: Mapped[Optional[str]] = mapped_column(String(50))  # positive, negative, neutral
    priority: Mapped[Optional[str]] = mapped_column(String(50))  # low, medium, high, urgent
    
    # LLM metadata
    model_used: Mapped[str] = mapped_column(String(100), default="claude-3-sonnet")
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Calendar sync status
    calendar_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    calendar_event_ids: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    
    # Relationship
    email: Mapped["Email"] = relationship("Email", back_populates="summaries")
    
    # Table indexes
    __table_args__ = (
        Index("idx_email_summaries_email_id", "email_id"),
        Index("idx_email_summaries_priority", "priority"),
    )
    
    def __repr__(self) -> str:
        return f"<EmailSummary {self.id} for Email {self.email_id}>"
