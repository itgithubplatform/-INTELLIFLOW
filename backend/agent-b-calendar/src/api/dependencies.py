"""
FastAPI Dependencies
====================

Dependency injection for Agent B services.
"""

from functools import lru_cache

from ..services.calendar_service import CalendarService
from ..core.config import agent_settings


@lru_cache
def get_calendar_service() -> CalendarService:
    """Get Calendar service instance."""
    return CalendarService()
