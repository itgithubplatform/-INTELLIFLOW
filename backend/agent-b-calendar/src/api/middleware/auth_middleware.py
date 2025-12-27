"""
Authentication Middleware
=========================

Middleware for validating tokens and enforcing authentication.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from shared.utils import get_logger

logger = get_logger(__name__)


class TokenValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs requests and validates token presence.
    
    Note: Actual token validation is done by the `validate_token` dependency.
    This middleware provides logging and can enforce token presence for
    non-public endpoints.
    """
    
    # Paths that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/health",
        "/api/v1/ready",
    }
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response]
    ) -> Response:
        """Process request and log authentication info."""
        
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        # Extract client info
        client_host = request.client.host if request.client else "unknown"
        source_agent = request.headers.get("X-Source-Agent", "direct")
        is_delegation = request.headers.get("X-Delegation", "false") == "true"
        
        # Check for auth header
        auth_header = request.headers.get("Authorization", "")
        has_token = auth_header.startswith("Bearer ")
        
        # Log request
        logger.info(
            "Incoming request",
            method=method,
            path=path,
            client=client_host,
            source_agent=source_agent,
            is_delegation=is_delegation,
            has_auth=has_token
        )
        
        # Check if path requires auth
        if path not in self.PUBLIC_PATHS and not has_token:
            # Let the endpoint's Depends handle the actual error
            # This is just for logging purposes
            logger.warning(
                "Request without auth token to protected path",
                path=path
            )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            duration = (time.time() - start_time) * 1000
            logger.info(
                "Request completed",
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration, 2)
            )
            
            # Add timing header
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"
            
            return response
            
        except Exception as e:
            logger.error(
                "Request failed with exception",
                method=method,
                path=path,
                error=str(e)
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
