"""
Scope Definitions and Enforcement
=================================

Defines OAuth scopes and provides utilities for scope-based authorization.
"""

from enum import Enum
from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, status

from .token_validator import TokenClaims, validate_token
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Scope(str, Enum):
    """
    OAuth scopes for IntelliFlow.
    
    Scopes follow the format: resource.action
    """
    
    # Email scopes (Agent A)
    EMAIL_READ = "email.read"
    EMAIL_SUMMARIZE = "email.summarize"
    
    # Calendar scopes (Agent B)
    CALENDAR_READ = "calendar.read"
    CALENDAR_WRITE = "calendar.write"
    
    # User profile scopes
    PROFILE_READ = "profile.read"
    PROFILE_WRITE = "profile.write"
    
    # Admin scopes
    ADMIN_READ = "admin.read"
    ADMIN_WRITE = "admin.write"
    
    def __str__(self) -> str:
        return self.value


# Scope descriptions for documentation
SCOPE_DESCRIPTIONS = {
    Scope.EMAIL_READ: "Read user's email messages and threads",
    Scope.EMAIL_SUMMARIZE: "Generate AI summaries of email content",
    Scope.CALENDAR_READ: "Read user's calendar events",
    Scope.CALENDAR_WRITE: "Create, modify, or delete calendar events",
    Scope.PROFILE_READ: "Read user profile information",
    Scope.PROFILE_WRITE: "Modify user profile settings",
    Scope.ADMIN_READ: "Read administrative data",
    Scope.ADMIN_WRITE: "Perform administrative actions",
}


class ScopeChecker:
    """
    Utility class for checking scopes.
    
    Can be used as a FastAPI dependency to enforce scope requirements.
    """
    
    def __init__(
        self,
        required_scopes: list[Scope],
        require_all: bool = True
    ):
        """
        Initialize scope checker.
        
        Args:
            required_scopes: List of scopes to check for
            require_all: If True, all scopes must be present.
                        If False, at least one scope must be present.
        """
        self.required_scopes = [str(scope) for scope in required_scopes]
        self.require_all = require_all
    
    async def __call__(
        self,
        claims: TokenClaims = Depends(validate_token)
    ) -> TokenClaims:
        """
        Check if token has required scopes.
        
        Args:
            claims: Validated token claims
            
        Returns:
            Token claims if scope check passes
            
        Raises:
            HTTPException: If scope check fails
        """
        user_scopes = claims.scopes
        
        if self.require_all:
            missing = [
                scope for scope in self.required_scopes
                if scope not in user_scopes
            ]
            if missing:
                logger.warning(
                    f"Scope check failed for user {claims.sub}. "
                    f"Missing scopes: {missing}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scopes: {', '.join(missing)}"
                )
        else:
            has_any = any(
                scope in user_scopes
                for scope in self.required_scopes
            )
            if not has_any:
                logger.warning(
                    f"Scope check failed for user {claims.sub}. "
                    f"Requires at least one of: {self.required_scopes}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires at least one of: {', '.join(self.required_scopes)}"
                )
        
        return claims


def require_scope(*scopes: Scope, require_all: bool = True):
    """
    FastAPI dependency factory for scope requirements.
    
    Usage:
        @app.post("/calendar/events")
        async def create_event(
            request: CreateEventRequest,
            claims: TokenClaims = Depends(require_scope(Scope.CALENDAR_WRITE))
        ):
            ...
    
    Args:
        scopes: Required scopes
        require_all: If True, all scopes must be present
        
    Returns:
        ScopeChecker dependency
    """
    return ScopeChecker(list(scopes), require_all=require_all)


def check_scope(claims: TokenClaims, scope: Scope) -> bool:
    """
    Simple function to check if claims include a scope.
    
    Args:
        claims: Token claims
        scope: Scope to check
        
    Returns:
        True if scope is present
    """
    return str(scope) in claims.scopes


def get_allowed_scopes(claims: TokenClaims) -> list[Scope]:
    """
    Get list of Scope enums that match the user's scopes.
    
    Args:
        claims: Token claims
        
    Returns:
        List of matching Scope enums
    """
    return [
        scope for scope in Scope
        if str(scope) in claims.scopes
    ]


# Pre-built dependencies for common scope requirements
require_email_read = require_scope(Scope.EMAIL_READ)
require_email_summarize = require_scope(Scope.EMAIL_READ, Scope.EMAIL_SUMMARIZE)
require_calendar_read = require_scope(Scope.CALENDAR_READ)
require_calendar_write = require_scope(Scope.CALENDAR_WRITE)
