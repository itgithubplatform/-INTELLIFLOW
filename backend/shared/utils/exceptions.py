"""
Custom Exceptions
=================

Custom exception classes for IntelliFlow.
"""

from typing import Any, Optional


class IntelliFlowError(Exception):
    """
    Base exception for all IntelliFlow errors.
    
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        message: str,
        code: str = "INTELLIFLOW_ERROR",
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class AuthenticationError(IntelliFlowError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(IntelliFlowError):
    """Raised when authorization fails (insufficient permissions)."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_scopes: list[str] = None,
        details: dict = None
    ):
        details = details or {}
        if required_scopes:
            details["required_scopes"] = required_scopes
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            details=details
        )


class TokenExchangeError(IntelliFlowError):
    """Raised when token exchange fails."""
    
    def __init__(
        self,
        message: str = "Token exchange failed",
        target_agent: str = None,
        details: dict = None
    ):
        details = details or {}
        if target_agent:
            details["target_agent"] = target_agent
        super().__init__(
            message=message,
            code="TOKEN_EXCHANGE_ERROR",
            details=details
        )


class ValidationError(IntelliFlowError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: str = None,
        details: dict = None
    ):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(IntelliFlowError):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: str = None,
        resource_id: str = None,
        details: dict = None
    ):
        details = details or {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        super().__init__(
            message=message,
            code="NOT_FOUND_ERROR",
            details=details
        )


class ExternalServiceError(IntelliFlowError):
    """Raised when an external service call fails."""
    
    def __init__(
        self,
        message: str = "External service error",
        service: str = None,
        status_code: int = None,
        details: dict = None
    ):
        details = details or {}
        if service:
            details["service"] = service
        if status_code:
            details["status_code"] = status_code
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            details=details
        )


class RateLimitError(IntelliFlowError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = None,
        details: dict = None
    ):
        details = details or {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            details=details
        )


class AgentCommunicationError(IntelliFlowError):
    """Raised when agent-to-agent communication fails."""
    
    def __init__(
        self,
        message: str = "Agent communication failed",
        source_agent: str = None,
        target_agent: str = None,
        details: dict = None
    ):
        details = details or {}
        if source_agent:
            details["source_agent"] = source_agent
        if target_agent:
            details["target_agent"] = target_agent
        super().__init__(
            message=message,
            code="AGENT_COMMUNICATION_ERROR",
            details=details
        )
