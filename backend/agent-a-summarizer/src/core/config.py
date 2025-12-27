"""
Agent A Configuration
=====================

Agent-specific configuration extending shared settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentASettings(BaseSettings):
    """Settings specific to Agent A - Email Summarizer."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Agent identity
    agent_id: str = Field(default="agent-a-summarizer")
    agent_name: str = Field(default="Email Summarizer")
    
    # Agent B URL for delegation
    agent_b_url: str = Field(
        default="http://localhost:8002",
        description="URL of Agent B (Calendar Manager)"
    )
    
    # Descope Inbound App for this agent
    inbound_app_id: str = Field(
        default="agent-a-summarizer",
        description="Descope Inbound App ID for this agent"
    )
    
    # Email processing settings
    max_emails_per_request: int = Field(default=50)
    email_batch_size: int = Field(default=10)
    
    # Summarization settings
    summary_max_length: int = Field(default=500)
    include_action_items: bool = Field(default=True)
    include_calendar_detection: bool = Field(default=True)
    
    # Celery settings
    celery_broker_url: Optional[str] = Field(default=None)
    celery_result_backend: Optional[str] = Field(default=None)


@lru_cache
def get_agent_settings() -> AgentASettings:
    """Get cached agent settings."""
    return AgentASettings()


agent_settings = get_agent_settings()
