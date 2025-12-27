"""
Scope Enforcement
=================

Scope definitions and enforcement for Agent B.
"""

from enum import Enum
from typing import List

from fastapi import HTTPException, status

from shared.auth import TokenClaims
from shared.utils import get_logger

logger = get_logger(__name__)


class CalendarScope(str, Enum):
    """Calendar-specific scopes for Agent B."""
    
    READ = "calendar.read"
    WRITE = "calendar.write"


def enforce_scope(claims: TokenClaims, required_scope: CalendarScope) -> None:
    """
    Enforce that a token has the required scope.
    
    Args:
        claims: Validated token claims
        required_scope: Required scope
        
    Raises:
        HTTPException: If scope is missing
    """
    if str(required_scope) not in claims.scopes:
        logger.warning(
            f"Scope enforcement failed",
            user_id=claims.sub,
            required_scope=str(required_scope),
            available_scopes=claims.scopes
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing required scope: {required_scope}"
        )


def validate_delegation(
    claims: TokenClaims,
    allowed_agents: List[str]
) -> None:
    """
    Validate that a delegated token comes from an allowed agent.
    
    Args:
        claims: Token claims
        allowed_agents: List of allowed source agent IDs
        
    Raises:
        HTTPException: If delegation is not valid
    """
    if claims.delegation:
        # Check if the delegating agent is allowed
        delegator = claims.delegator or claims.azp
        
        if delegator not in allowed_agents:
            logger.warning(
                f"Delegation rejected from unknown agent",
                delegator=delegator,
                allowed_agents=allowed_agents
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Delegation from '{delegator}' is not allowed"
            )
        
        logger.info(
            f"Delegation accepted from {delegator}",
            user_id=claims.sub
        )
