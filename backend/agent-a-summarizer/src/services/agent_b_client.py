"""
Agent B Client
==============

HTTP client for communicating with Agent B (Calendar Manager).
Handles token delegation and secure API calls.
"""

from typing import Any, Optional

import httpx

from shared.auth import TokenClaims, DescopeClient, get_descope_client
from shared.utils import get_logger
from shared.utils.exceptions import AgentCommunicationError, TokenExchangeError

logger = get_logger(__name__)


class AgentBClient:
    """
    Client for secure communication with Agent B.
    
    Handles:
    - Token delegation via Descope
    - Secure API calls to Agent B endpoints
    - Event creation delegation
    """
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        """
        Initialize Agent B client.
        
        Args:
            base_url: Base URL of Agent B service
        """
        self.base_url = base_url.rstrip("/")
        self._http_client: Optional[httpx.AsyncClient] = None
        self._descope_client: Optional[DescopeClient] = None
    
    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers={"Content-Type": "application/json"}
            )
        return self._http_client
    
    @property
    def descope_client(self) -> DescopeClient:
        """Get Descope client for token delegation."""
        if self._descope_client is None:
            self._descope_client = get_descope_client()
        return self._descope_client
    
    async def close(self):
        """Close HTTP client connections."""
        if self._http_client:
            await self._http_client.aclose()
    
    async def get_delegated_token(
        self,
        user_claims: TokenClaims,
        scopes: list[str]
    ) -> str:
        """
        Get a delegated token for calling Agent B.
        
        This creates a new token with reduced scopes that Agent B
        can use to act on behalf of the user.
        
        Args:
            user_claims: Current user's token claims
            scopes: Scopes to request for Agent B
            
        Returns:
            Delegated access token
        """
        logger.info(
            f"Requesting delegated token for Agent B",
            user_id=user_claims.sub,
            requested_scopes=scopes
        )
        
        try:
            # Create delegated token via Descope
            delegated_token = await self.descope_client.create_delegated_token(
                user_id=user_claims.sub,
                target_agent="agent-b-calendar",
                scopes=scopes,
                expiry_seconds=3600  # 1 hour expiry
            )
            
            logger.info("Delegated token created successfully")
            return delegated_token
            
        except Exception as e:
            logger.error(f"Failed to create delegated token: {e}")
            raise TokenExchangeError(
                message=f"Failed to delegate access to Agent B: {str(e)}",
                target_agent="agent-b-calendar"
            )
    
    async def create_event(
        self,
        token: str,
        event_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Create a calendar event via Agent B.
        
        Args:
            token: Delegated access token
            event_data: Event details (title, date, time, etc.)
            
        Returns:
            Created event data or None if failed
        """
        logger.info(
            f"Creating calendar event via Agent B",
            event_title=event_data.get("title")
        )
        
        try:
            response = await self.http_client.post(
                "/api/v1/calendar/events",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Source-Agent": "agent-a-summarizer",
                    "X-Delegation": "true"
                },
                json=event_data
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(
                    f"Calendar event created successfully",
                    event_id=data.get("id")
                )
                return data
            
            elif response.status_code == 401:
                raise TokenExchangeError(
                    message="Delegated token was rejected by Agent B",
                    target_agent="agent-b-calendar"
                )
            
            elif response.status_code == 403:
                raise AgentCommunicationError(
                    message="Insufficient scopes for calendar.write",
                    source_agent="agent-a-summarizer",
                    target_agent="agent-b-calendar"
                )
            
            else:
                error_data = response.json() if response.content else {}
                logger.error(
                    f"Failed to create event: {response.status_code}",
                    error=error_data
                )
                return None
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Agent B: {e}")
            raise AgentCommunicationError(
                message=f"Failed to communicate with Agent B: {str(e)}",
                source_agent="agent-a-summarizer",
                target_agent="agent-b-calendar"
            )
    
    async def check_health(self) -> bool:
        """
        Check if Agent B is healthy.
        
        Returns:
            True if Agent B is responding
        """
        try:
            response = await self.http_client.get("/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_user_calendar(
        self,
        token: str,
        start_date: str = None,
        end_date: str = None
    ) -> list[dict[str, Any]]:
        """
        Fetch user's calendar events via Agent B.
        
        Args:
            token: Delegated access token with calendar.read scope
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            List of calendar events
        """
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            response = await self.http_client.get(
                "/api/v1/calendar/events",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Source-Agent": "agent-a-summarizer"
                },
                params=params
            )
            
            if response.status_code == 200:
                return response.json().get("events", [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching calendar: {e}")
            return []
