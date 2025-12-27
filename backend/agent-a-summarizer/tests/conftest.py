"""
Test Configuration
==================

Pytest fixtures and configuration for Agent A tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail service."""
    service = MagicMock()
    service.list_emails = AsyncMock(return_value={
        "emails": [
            {
                "id": "msg_1",
                "subject": "Test Email",
                "sender": "test@example.com",
                "snippet": "This is a test email..."
            }
        ],
        "next_page_token": None,
        "total_count": 1
    })
    service.get_email = AsyncMock(return_value={
        "id": "msg_1",
        "subject": "Test Email",
        "sender": "test@example.com",
        "body": "This is the full email body."
    })
    return service


@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    service = MagicMock()
    service.summarize_email = AsyncMock(return_value={
        "summary": "This is a test summary.",
        "key_points": ["Point 1", "Point 2"],
        "action_items": [],
        "detected_events": [],
        "sentiment": "neutral",
        "priority": "medium"
    })
    return service


@pytest.fixture
def mock_agent_b_client():
    """Mock Agent B client."""
    client = MagicMock()
    client.get_delegated_token = AsyncMock(return_value="mock_delegated_token")
    client.create_event = AsyncMock(return_value={"id": "event_1", "title": "Test Event"})
    client.check_health = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_token_claims():
    """Mock token claims for authenticated requests."""
    return {
        "sub": "user_123",
        "email": "user@example.com",
        "scopes": ["email.read", "email.summarize"],
        "exp": 9999999999
    }
