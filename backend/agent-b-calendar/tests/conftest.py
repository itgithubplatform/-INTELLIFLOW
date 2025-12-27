"""
Test Configuration
==================

Pytest fixtures and configuration for Agent B tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_calendar_service():
    """Mock Calendar service."""
    service = MagicMock()
    service.list_events = AsyncMock(return_value=[
        {
            "id": "event_1",
            "title": "Test Event",
            "start_time": "2024-01-15T10:00:00Z",
            "end_time": "2024-01-15T11:00:00Z"
        }
    ])
    service.create_event = AsyncMock(return_value={
        "id": "event_new",
        "title": "New Event",
        "start_time": "2024-01-15T14:00:00Z",
        "end_time": "2024-01-15T15:00:00Z"
    })
    service.get_event = AsyncMock(return_value={
        "id": "event_1",
        "title": "Test Event"
    })
    service.update_event = AsyncMock(return_value={
        "id": "event_1",
        "title": "Updated Event"
    })
    service.delete_event = AsyncMock(return_value=True)
    return service


@pytest.fixture
def mock_token_claims():
    """Mock token claims for authenticated requests."""
    return {
        "sub": "user_123",
        "email": "user@example.com",
        "scopes": ["calendar.read", "calendar.write"],
        "exp": 9999999999,
        "delegation": False
    }


@pytest.fixture
def mock_delegated_token_claims():
    """Mock delegated token claims from Agent A."""
    return {
        "sub": "user_123",
        "email": "user@example.com",
        "scopes": ["calendar.write"],
        "exp": 9999999999,
        "delegation": True,
        "delegator": "agent-a-summarizer",
        "azp": "agent-a-summarizer"
    }
