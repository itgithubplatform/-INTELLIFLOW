"""
FastAPI Dependencies
====================

Dependency injection for Agent A services.
"""

from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends

from shared.auth import TokenClaims, validate_token
from shared.database import get_db_session

from ..services.gmail_service import GmailService
from ..services.llm_service import LLMService
from ..services.agent_b_client import AgentBClient
from ..core.config import agent_settings


@lru_cache
def get_gmail_service() -> GmailService:
    """Get Gmail service instance."""
    return GmailService()


@lru_cache
def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    return LLMService()


@lru_cache
def get_agent_b_client() -> AgentBClient:
    """Get Agent B client instance."""
    return AgentBClient(
        base_url=agent_settings.agent_b_url
    )
