"""
Agent B Configuration
=====================

Agent-specific configuration extending shared settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentBSettings(BaseSettings):
    """Settings specific to Agent B - Calendar Manager."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Agent identity
    agent_id: str = Field(default="agent-b-calendar")
    agent_name: str = Field(default="Calendar Manager")
    
    # Descope Inbound App for this agent
    inbound_app_id: str = Field(
        default="agent-b-calendar",
        description="Descope Inbound App ID for this agent"
    )
    
    # Calendar settings
    default_event_duration: int = Field(default=60, description="Default event duration in minutes")
    max_events_per_request: int = Field(default=50)
    default_calendar_id: str = Field(default="primary")
    
    # Allowed source agents for delegation
    allowed_source_agents: list[str] = Field(
        default=["agent-a-summarizer"],
        description="List of agents allowed to delegate to this agent"
    )


@lru_cache
def get_agent_settings() -> AgentBSettings:
    """Get cached agent settings."""
    return AgentBSettings()


agent_settings = get_agent_settings()
