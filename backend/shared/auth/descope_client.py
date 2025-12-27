"""
Descope Client
==============

Wrapper around the Descope SDK for authentication operations.
Handles token exchange, refresh, and user management.
"""

import asyncio
from functools import lru_cache
from typing import Any, Optional

import httpx
from descope import (
    REFRESH_SESSION_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    AuthException,
    DescopeClient as BaseDescopeClient,
)

from ..config import settings
from ..utils.logger import get_logger
from ..utils.exceptions import AuthenticationError, TokenExchangeError

logger = get_logger(__name__)


class DescopeClient:
    """
    Enhanced Descope client for IntelliFlow.
    
    Provides methods for:
    - Token validation
    - Token exchange for agent-to-agent communication
    - User session management
    - Scope-based authorization
    """
    
    def __init__(self, project_id: str, management_key: Optional[str] = None):
        """
        Initialize Descope client.
        
        Args:
            project_id: Descope project ID
            management_key: Optional management key for admin operations
        """
        self.project_id = project_id
        self.management_key = management_key
        self._client: Optional[BaseDescopeClient] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        
    @property
    def client(self) -> BaseDescopeClient:
        """Get or create the Descope client instance."""
        if self._client is None:
            self._client = BaseDescopeClient(
                project_id=self.project_id,
                management_key=self.management_key
            )
        return self._client
    
    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client for custom API calls."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=settings.descope.base_url,
                timeout=30.0
            )
        return self._http_client
    
    async def close(self):
        """Close HTTP client connections."""
        if self._http_client:
            await self._http_client.aclose()
    
    def validate_session(self, session_token: str) -> dict[str, Any]:
        """
        Validate a session token.
        
        Args:
            session_token: JWT session token
            
        Returns:
            Decoded token claims
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            return self.client.validate_session(session_token)
        except AuthException as e:
            logger.warning(f"Session validation failed: {e}")
            raise AuthenticationError(f"Invalid session token: {e}")
    
    def validate_and_refresh_session(
        self,
        session_token: str,
        refresh_token: str
    ) -> dict[str, Any]:
        """
        Validate and optionally refresh a session.
        
        Args:
            session_token: JWT session token
            refresh_token: Refresh token
            
        Returns:
            Token claims with potentially refreshed tokens
        """
        try:
            return self.client.validate_and_refresh_session(
                session_token,
                refresh_token
            )
        except AuthException as e:
            logger.warning(f"Session refresh failed: {e}")
            raise AuthenticationError(f"Session refresh failed: {e}")
    
    async def exchange_token(
        self,
        access_token: str,
        target_app_id: str,
        scopes: list[str],
        options: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Exchange access token for a new token with specific scopes.
        
        This is used for agent-to-agent delegation, where Agent A
        requests a scoped token to call Agent B's API.
        
        Args:
            access_token: Current access token
            target_app_id: Target inbound app ID
            scopes: List of requested scopes
            options: Additional exchange options
            
        Returns:
            New token response with delegated access
            
        Raises:
            TokenExchangeError: If exchange fails
        """
        try:
            # Use Descope's token exchange endpoint
            response = await self.http_client.post(
                f"/v1/auth/accesskey/exchange",
                headers={
                    "Authorization": f"Bearer {self.project_id}",
                    "Content-Type": "application/json"
                },
                json={
                    "accessToken": access_token,
                    "targetAppId": target_app_id,
                    "scopes": scopes,
                    **(options or {})
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                raise TokenExchangeError(
                    f"Token exchange failed: {error_data.get('message', 'Unknown error')}"
                )
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {e}")
            raise TokenExchangeError(f"Token exchange request failed: {e}")
    
    async def create_delegated_token(
        self,
        user_id: str,
        target_agent: str,
        scopes: list[str],
        expiry_seconds: int = 3600
    ) -> str:
        """
        Create a delegated token for agent-to-agent communication.
        
        Args:
            user_id: User ID on whose behalf we're acting
            target_agent: Target agent's inbound app ID
            scopes: Scopes to include in the delegated token
            expiry_seconds: Token expiry time
            
        Returns:
            Delegated access token
        """
        try:
            # Use management API to create delegated token
            response = await self.http_client.post(
                f"/v1/mgmt/accesskey/create",
                headers={
                    "Authorization": f"Bearer {self.management_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": f"delegated-{target_agent}-{user_id}",
                    "expireTime": expiry_seconds,
                    "userId": user_id,
                    "customClaims": {
                        "scopes": scopes,
                        "target_agent": target_agent,
                        "delegation": True
                    }
                }
            )
            
            if response.status_code != 200:
                raise TokenExchangeError("Failed to create delegated token")
            
            data = response.json()
            return data.get("cleartext", data.get("key", ""))
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create delegated token: {e}")
            raise TokenExchangeError(f"Delegation failed: {e}")
    
    def get_user_scopes(self, token_claims: dict[str, Any]) -> list[str]:
        """
        Extract scopes from token claims.
        
        Args:
            token_claims: Decoded JWT claims
            
        Returns:
            List of granted scopes
        """
        # Check multiple possible locations for scopes
        if "scopes" in token_claims:
            return token_claims["scopes"]
        if "scope" in token_claims:
            scope = token_claims["scope"]
            if isinstance(scope, str):
                return scope.split()
            return scope
        if "permissions" in token_claims:
            return token_claims["permissions"]
        return []
    
    def has_scope(self, token_claims: dict[str, Any], required_scope: str) -> bool:
        """
        Check if token has a specific scope.
        
        Args:
            token_claims: Decoded JWT claims
            required_scope: Scope to check for
            
        Returns:
            True if scope is present
        """
        scopes = self.get_user_scopes(token_claims)
        return required_scope in scopes


@lru_cache
def get_descope_client() -> DescopeClient:
    """Get cached Descope client instance."""
    return DescopeClient(
        project_id=settings.descope.project_id,
        management_key=settings.descope.management_key
    )
