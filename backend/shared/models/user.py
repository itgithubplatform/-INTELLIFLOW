"""
User Model
==========

User and authentication-related models.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class AuthProvider(str, Enum):
    """Authentication provider types."""
    DESCOPE = "descope"
    GOOGLE = "google"


class User(Base, TimestampMixin):
    """
    User model for IntelliFlow.
    
    Stores user profile information and OAuth connections.
    """
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    picture: Mapped[Optional[str]] = mapped_column(Text)
    
    # OAuth connections
    descope_user_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    google_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    google_email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Settings stored as JSON
    preferences: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    tokens: Mapped[list["UserToken"]] = relationship(
        "UserToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Table indexes
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_descope_id", "descope_user_id"),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"


class UserToken(Base, TimestampMixin):
    """
    Stores OAuth tokens for external services.
    
    Used for Gmail and Google Calendar API access.
    """
    
    __tablename__ = "user_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Token details
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    token_type: Mapped[str] = mapped_column(String(50), default="Bearer")
    
    # Scopes granted
    scopes: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    
    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="tokens")
    
    # Table indexes
    __table_args__ = (
        Index("idx_user_tokens_user_provider", "user_id", "provider"),
    )
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(self.expires_at.tzinfo) > self.expires_at
    
    def __repr__(self) -> str:
        return f"<UserToken {self.provider} for {self.user_id}>"
