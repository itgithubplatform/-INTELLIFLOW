"""
Token Validator
===============

JWT token validation utilities using Descope's JWKS.
Provides FastAPI dependencies for authentication.
"""

from typing import Any, Optional

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from pydantic import BaseModel

from ..config import settings
from ..utils.logger import get_logger
from ..utils.exceptions import AuthenticationError

logger = get_logger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


class TokenClaims(BaseModel):
    """Validated token claims."""
    
    sub: str  # Subject (user ID)
    iss: str  # Issuer
    aud: Optional[str] = None  # Audience
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    azp: Optional[str] = None  # Authorized party (client ID)
    scopes: list[str] = []  # Granted scopes
    email: Optional[str] = None
    name: Optional[str] = None
    delegation: bool = False  # Whether this is a delegated token
    delegator: Optional[str] = None  # Original user who delegated
    
    class Config:
        extra = "allow"  # Allow additional claims


class TokenValidator:
    """
    JWT token validator using Descope's JWKS.
    
    Caches the JWKS and provides validation methods.
    """
    
    def __init__(self, project_id: str):
        """
        Initialize token validator.
        
        Args:
            project_id: Descope project ID
        """
        self.project_id = project_id
        self._jwks: Optional[dict] = None
        self._jwks_uri = f"https://api.descope.com/{project_id}/.well-known/jwks.json"
    
    async def _fetch_jwks(self) -> dict:
        """Fetch JWKS from Descope."""
        async with httpx.AsyncClient() as client:
            response = await client.get(self._jwks_uri)
            response.raise_for_status()
            return response.json()
    
    async def get_jwks(self) -> dict:
        """Get JWKS, fetching if not cached."""
        if self._jwks is None:
            self._jwks = await self._fetch_jwks()
        return self._jwks
    
    async def validate_token(self, token: str) -> TokenClaims:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Validated token claims
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # Get JWKS for signature verification
            jwks = await self.get_jwks()
            
            # Decode header to get key ID
            unverified_headers = jwt.get_unverified_headers(token)
            kid = unverified_headers.get("kid")
            
            # Find matching key
            rsa_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    rsa_key = key
                    break
            
            if not rsa_key:
                raise AuthenticationError("Unable to find matching key")
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[settings.app.jwt_algorithm],
                audience=self.project_id,
                issuer=f"https://api.descope.com/{self.project_id}"
            )
            
            # Extract scopes from various possible locations
            scopes = []
            if "scopes" in payload:
                scopes = payload["scopes"]
            elif "scope" in payload:
                scope = payload["scope"]
                scopes = scope.split() if isinstance(scope, str) else scope
            elif "permissions" in payload:
                scopes = payload["permissions"]
            
            # Build claims object
            claims = TokenClaims(
                sub=payload.get("sub", ""),
                iss=payload.get("iss", ""),
                aud=payload.get("aud"),
                exp=payload.get("exp", 0),
                iat=payload.get("iat", 0),
                azp=payload.get("azp"),
                scopes=scopes,
                email=payload.get("email"),
                name=payload.get("name"),
                delegation=payload.get("delegation", False),
                delegator=payload.get("delegator"),
            )
            
            return claims
            
        except ExpiredSignatureError:
            logger.warning("Token has expired")
            raise AuthenticationError("Token has expired")
        except JWTError as e:
            logger.warning(f"JWT validation error: {e}")
            raise AuthenticationError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            raise AuthenticationError("Token validation failed")
    
    def validate_scopes(
        self,
        claims: TokenClaims,
        required_scopes: list[str]
    ) -> bool:
        """
        Validate that token has required scopes.
        
        Args:
            claims: Token claims
            required_scopes: List of required scopes
            
        Returns:
            True if all required scopes are present
        """
        return all(scope in claims.scopes for scope in required_scopes)


# Global validator instance
_validator: Optional[TokenValidator] = None


def get_validator() -> TokenValidator:
    """Get or create token validator instance."""
    global _validator
    if _validator is None:
        _validator = TokenValidator(settings.descope.project_id)
    return _validator


async def validate_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenClaims:
    """
    FastAPI dependency for token validation.
    
    Usage:
        @app.get("/protected")
        async def protected_route(claims: TokenClaims = Depends(validate_token)):
            return {"user_id": claims.sub}
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    validator = get_validator()
    
    try:
        claims = await validator.validate_token(credentials.credentials)
        return claims
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    claims: TokenClaims = Depends(validate_token)
) -> dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    Returns user information from validated token claims.
    """
    return {
        "user_id": claims.sub,
        "email": claims.email,
        "name": claims.name,
        "scopes": claims.scopes,
        "is_delegated": claims.delegation,
    }
