"""
Authentication Module
=====================

Descope integration for OAuth-based authentication and authorization.
Includes token validation, scope enforcement, and delegation support.
"""

from .descope_client import DescopeClient, get_descope_client
from .token_validator import TokenValidator, validate_token, get_current_user
from .scopes import Scope, ScopeChecker, require_scope

__all__ = [
    "DescopeClient",
    "get_descope_client",
    "TokenValidator",
    "validate_token",
    "get_current_user",
    "Scope",
    "ScopeChecker",
    "require_scope",
]
