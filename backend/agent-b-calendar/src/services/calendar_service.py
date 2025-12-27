"""
Calendar Service
================

Integration with Google Calendar API for event management.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from shared.utils import get_logger
from shared.utils.exceptions import ExternalServiceError, NotFoundError

from ..core.config import agent_settings

logger = get_logger(__name__)


class CalendarService:
    """
    Service for interacting with Google Calendar API.
    
    Handles authentication, CRUD operations for events, and syncing.
    """
    
    def __init__(self):
        """Initialize Calendar service."""
        self._service_cache: dict[str, Any] = {}
        self._local_events: dict[str, list[dict]] = {}  # In-memory storage for demo
    
    async def _get_service(self, user_id: str, access_token: str = None):
        """
        Get Google Calendar API service instance for a user.
        
        Args:
            user_id: User ID
            access_token: Google OAuth access token
            
        Returns:
            Calendar API service or None for mock mode
        """
        if not access_token:
            return None  # Use mock mode
        
        cache_key = f"{user_id}_{access_token[:20]}"
        
        if cache_key not in self._service_cache:
            credentials = Credentials(token=access_token)
            self._service_cache[cache_key] = build(
                "calendar",
                "v3",
                credentials=credentials,
                cache_discovery=False
            )
        
        return self._service_cache[cache_key]
    
    async def list_events(
        self,
        user_id: str,
        access_token: str = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 50,
        calendar_id: str = "primary"
    ) -> list[dict[str, Any]]:
        """
        List calendar events for a user.
        
        Args:
            user_id: User ID
            access_token: Google OAuth access token (optional for mock)
            start_date: Filter start date (YYYY-MM-DD)
            end_date: Filter end date (YYYY-MM-DD)
            max_results: Maximum results
            calendar_id: Google Calendar ID
            
        Returns:
            List of calendar events
        """
        # Mock mode for development/testing
        if not access_token:
            return self._get_mock_events(user_id, start_date, end_date)
        
        try:
            service = await self._get_service(user_id, access_token)
            
            # Build request parameters
            params = {
                "calendarId": calendar_id,
                "maxResults": max_results,
                "singleEvents": True,
                "orderBy": "startTime"
            }
            
            if start_date:
                params["timeMin"] = f"{start_date}T00:00:00Z"
            else:
                params["timeMin"] = datetime.utcnow().isoformat() + "Z"
            
            if end_date:
                params["timeMax"] = f"{end_date}T23:59:59Z"
            
            # Fetch events
            response = service.events().list(**params).execute()
            events = response.get("items", [])
            
            # Transform to our format
            return [self._transform_google_event(e) for e in events]
            
        except Exception as e:
            logger.error(f"Error listing calendar events: {e}")
            raise ExternalServiceError(
                message=f"Failed to list events: {str(e)}",
                service="google_calendar"
            )
    
    async def create_event(
        self,
        user_id: str,
        event_data: dict[str, Any],
        access_token: str = None,
        calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """
        Create a new calendar event.
        
        Args:
            user_id: User ID
            event_data: Event details
            access_token: Google OAuth access token
            calendar_id: Google Calendar ID
            
        Returns:
            Created event data
        """
        logger.info(
            f"Creating calendar event",
            user_id=user_id,
            title=event_data.get("title")
        )
        
        # Mock mode for development/testing
        if not access_token:
            return self._create_mock_event(user_id, event_data)
        
        try:
            service = await self._get_service(user_id, access_token)
            
            # Build Google Calendar event body
            google_event = self._build_google_event(event_data)
            
            # Create event
            created = service.events().insert(
                calendarId=calendar_id,
                body=google_event
            ).execute()
            
            logger.info(
                f"Calendar event created",
                user_id=user_id,
                google_event_id=created.get("id")
            )
            
            return self._transform_google_event(created)
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            raise ExternalServiceError(
                message=f"Failed to create event: {str(e)}",
                service="google_calendar"
            )
    
    async def get_event(
        self,
        user_id: str,
        event_id: str,
        access_token: str = None,
        calendar_id: str = "primary"
    ) -> Optional[dict[str, Any]]:
        """
        Get a specific calendar event.
        
        Args:
            user_id: User ID
            event_id: Event ID
            access_token: Google OAuth access token
            calendar_id: Google Calendar ID
            
        Returns:
            Event data or None
        """
        # Mock mode
        if not access_token:
            return self._get_mock_event(user_id, event_id)
        
        try:
            service = await self._get_service(user_id, access_token)
            
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return self._transform_google_event(event)
            
        except Exception as e:
            if "404" in str(e):
                return None
            logger.error(f"Error fetching event {event_id}: {e}")
            raise ExternalServiceError(
                message=f"Failed to fetch event: {str(e)}",
                service="google_calendar"
            )
    
    async def update_event(
        self,
        user_id: str,
        event_id: str,
        event_data: dict[str, Any],
        access_token: str = None,
        calendar_id: str = "primary"
    ) -> Optional[dict[str, Any]]:
        """
        Update a calendar event.
        
        Args:
            user_id: User ID
            event_id: Event ID
            event_data: Updated event data
            access_token: Google OAuth access token
            calendar_id: Google Calendar ID
            
        Returns:
            Updated event data or None
        """
        # Mock mode
        if not access_token:
            return self._update_mock_event(user_id, event_id, event_data)
        
        try:
            service = await self._get_service(user_id, access_token)
            
            # Get existing event
            existing = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Merge updates
            google_event = self._build_google_event(event_data)
            for key, value in google_event.items():
                existing[key] = value
            
            # Update
            updated = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=existing
            ).execute()
            
            return self._transform_google_event(updated)
            
        except Exception as e:
            if "404" in str(e):
                return None
            logger.error(f"Error updating event {event_id}: {e}")
            raise ExternalServiceError(
                message=f"Failed to update event: {str(e)}",
                service="google_calendar"
            )
    
    async def delete_event(
        self,
        user_id: str,
        event_id: str,
        access_token: str = None,
        calendar_id: str = "primary"
    ) -> bool:
        """
        Delete a calendar event.
        
        Args:
            user_id: User ID
            event_id: Event ID
            access_token: Google OAuth access token
            calendar_id: Google Calendar ID
            
        Returns:
            True if deleted, False if not found
        """
        # Mock mode
        if not access_token:
            return self._delete_mock_event(user_id, event_id)
        
        try:
            service = await self._get_service(user_id, access_token)
            
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return True
            
        except Exception as e:
            if "404" in str(e):
                return False
            logger.error(f"Error deleting event {event_id}: {e}")
            raise ExternalServiceError(
                message=f"Failed to delete event: {str(e)}",
                service="google_calendar"
            )
    
    def _build_google_event(self, event_data: dict) -> dict:
        """Build Google Calendar API event body."""
        google_event = {
            "summary": event_data.get("title", "Untitled Event"),
        }
        
        if event_data.get("description"):
            google_event["description"] = event_data["description"]
        
        if event_data.get("location"):
            google_event["location"] = event_data["location"]
        
        # Handle datetime
        if event_data.get("is_all_day"):
            google_event["start"] = {"date": event_data["start_time"][:10]}
            google_event["end"] = {"date": event_data["end_time"][:10]}
        else:
            timezone = event_data.get("timezone", "UTC")
            start = event_data.get("start_time")
            end = event_data.get("end_time")
            
            if isinstance(start, datetime):
                start = start.isoformat()
            if isinstance(end, datetime):
                end = end.isoformat()
            
            google_event["start"] = {"dateTime": start, "timeZone": timezone}
            google_event["end"] = {"dateTime": end, "timeZone": timezone}
        
        # Attendees
        if event_data.get("attendees"):
            google_event["attendees"] = [
                {"email": a.get("email"), "displayName": a.get("name")}
                for a in event_data["attendees"]
            ]
        
        return google_event
    
    def _transform_google_event(self, google_event: dict) -> dict:
        """Transform Google Calendar event to our format."""
        start = google_event.get("start", {})
        end = google_event.get("end", {})
        
        return {
            "id": google_event.get("id"),
            "google_event_id": google_event.get("id"),
            "title": google_event.get("summary", "Untitled"),
            "description": google_event.get("description"),
            "location": google_event.get("location"),
            "start_time": start.get("dateTime") or start.get("date"),
            "end_time": end.get("dateTime") or end.get("date"),
            "timezone": start.get("timeZone", "UTC"),
            "is_all_day": "date" in start,
            "attendees": [
                {
                    "email": a.get("email"),
                    "name": a.get("displayName"),
                    "response_status": a.get("responseStatus", "needsAction")
                }
                for a in google_event.get("attendees", [])
            ],
            "status": google_event.get("status", "confirmed"),
            "source": "google_calendar",
            "created_at": google_event.get("created"),
            "updated_at": google_event.get("updated"),
            "is_synced": True,
            "last_synced_at": datetime.utcnow().isoformat()
        }
    
    # ==================== Mock Methods for Development ====================
    
    def _get_mock_events(
        self,
        user_id: str,
        start_date: str = None,
        end_date: str = None
    ) -> list[dict]:
        """Get mock events for development."""
        if user_id not in self._local_events:
            self._local_events[user_id] = self._generate_mock_events()
        return self._local_events[user_id]
    
    def _create_mock_event(self, user_id: str, event_data: dict) -> dict:
        """Create mock event."""
        if user_id not in self._local_events:
            self._local_events[user_id] = []
        
        event_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow().isoformat()
        
        event = {
            "id": event_id,
            "google_event_id": f"mock_{event_id}",
            "title": event_data.get("title", "Untitled"),
            "description": event_data.get("description"),
            "location": event_data.get("location"),
            "start_time": str(event_data.get("start_time")),
            "end_time": str(event_data.get("end_time")),
            "timezone": event_data.get("timezone", "UTC"),
            "is_all_day": event_data.get("is_all_day", False),
            "attendees": event_data.get("attendees", []),
            "status": "confirmed",
            "source": event_data.get("source", "user_created"),
            "created_at": now,
            "updated_at": now,
            "is_synced": False,
            "last_synced_at": None
        }
        
        self._local_events[user_id].append(event)
        return event
    
    def _get_mock_event(self, user_id: str, event_id: str) -> Optional[dict]:
        """Get single mock event."""
        events = self._local_events.get(user_id, [])
        for event in events:
            if event["id"] == event_id:
                return event
        return None
    
    def _update_mock_event(
        self,
        user_id: str,
        event_id: str,
        event_data: dict
    ) -> Optional[dict]:
        """Update mock event."""
        events = self._local_events.get(user_id, [])
        for i, event in enumerate(events):
            if event["id"] == event_id:
                for key, value in event_data.items():
                    if value is not None:
                        event[key] = value
                event["updated_at"] = datetime.utcnow().isoformat()
                self._local_events[user_id][i] = event
                return event
        return None
    
    def _delete_mock_event(self, user_id: str, event_id: str) -> bool:
        """Delete mock event."""
        events = self._local_events.get(user_id, [])
        for i, event in enumerate(events):
            if event["id"] == event_id:
                self._local_events[user_id].pop(i)
                return True
        return False
    
    def _generate_mock_events(self) -> list[dict]:
        """Generate sample mock events."""
        now = datetime.utcnow()
        return [
            {
                "id": "mock_1",
                "google_event_id": "mock_google_1",
                "title": "Team Standup",
                "description": "Daily team sync",
                "location": "Zoom",
                "start_time": (now + timedelta(days=1, hours=9)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=9, minutes=30)).isoformat(),
                "timezone": "UTC",
                "is_all_day": False,
                "attendees": [],
                "status": "confirmed",
                "source": "mock",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "is_synced": False
            },
            {
                "id": "mock_2",
                "google_event_id": "mock_google_2",
                "title": "Q1 Planning Session",
                "description": "Quarterly planning meeting",
                "location": "Conference Room A",
                "start_time": (now + timedelta(days=7, hours=14)).isoformat(),
                "end_time": (now + timedelta(days=7, hours=16)).isoformat(),
                "timezone": "UTC",
                "is_all_day": False,
                "attendees": [
                    {"email": "team@company.com", "name": "Team", "response_status": "accepted"}
                ],
                "status": "confirmed",
                "source": "mock",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "is_synced": False
            }
        ]
