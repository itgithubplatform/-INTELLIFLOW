"""
Logging Utilities
=================

Structured logging setup using structlog.
"""

import logging
import sys
from typing import Any

import structlog

from ..config import settings


def setup_logging(log_level: str = None) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Override log level (default: from settings)
    """
    level = log_level or settings.app.log_level
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if settings.app.debug:
        # Development: colorful console output
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        # Production: JSON output
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class LogContext:
    """
    Context manager for adding temporary context to logs.
    
    Usage:
        with LogContext(request_id="abc123", user_id="user1"):
            logger.info("Processing request")
    """
    
    def __init__(self, **context: Any):
        self.context = context
        self._tokens = []
    
    def __enter__(self):
        for key, value in self.context.items():
            token = structlog.contextvars.bind_contextvars(**{key: value})
            self._tokens.append((key, token))
        return self
    
    def __exit__(self, *args):
        for key, _ in reversed(self._tokens):
            structlog.contextvars.unbind_contextvars(key)


def log_request(
    method: str,
    path: str,
    user_id: str = None,
    **extra: Any
) -> None:
    """
    Log an API request.
    
    Args:
        method: HTTP method
        path: Request path
        user_id: Optional user ID
        extra: Additional context
    """
    logger = get_logger("api.request")
    logger.info(
        "API Request",
        method=method,
        path=path,
        user_id=user_id,
        **extra
    )


def log_response(
    status_code: int,
    duration_ms: float,
    **extra: Any
) -> None:
    """
    Log an API response.
    
    Args:
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        extra: Additional context
    """
    logger = get_logger("api.response")
    level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
    getattr(logger, level)(
        "API Response",
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **extra
    )
