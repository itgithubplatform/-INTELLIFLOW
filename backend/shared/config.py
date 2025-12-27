"""
Shared Configuration
====================

Central configuration management for all IntelliFlow services.
Uses pydantic-settings for environment variable loading and validation.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="")
    
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/intelliflow",
        description="PostgreSQL connection URL"
    )
    db_pool_size: int = Field(default=5, description="Connection pool size")
    db_max_overflow: int = Field(default=10, description="Max overflow connections")
    db_echo: bool = Field(default=False, description="Echo SQL statements")


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="")
    
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    redis_max_connections: int = Field(default=10, description="Max Redis connections")


class DescopeSettings(BaseSettings):
    """Descope authentication settings."""
    
    model_config = SettingsConfigDict(env_prefix="DESCOPE_")
    
    project_id: str = Field(
        default="",
        description="Descope Project ID"
    )
    management_key: Optional[str] = Field(
        default=None,
        description="Descope Management Key for admin operations"
    )
    base_url: str = Field(
        default="https://api.descope.com",
        description="Descope API base URL"
    )


class AnthropicSettings(BaseSettings):
    """Anthropic Claude API settings."""
    
    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_")
    
    api_key: str = Field(
        default="",
        description="Anthropic API Key"
    )
    model: str = Field(
        default="claude-3-sonnet-20240229",
        description="Claude model to use"
    )
    max_tokens: int = Field(
        default=4096,
        description="Maximum tokens in response"
    )


class GoogleSettings(BaseSettings):
    """Google API settings for Gmail and Calendar."""
    
    model_config = SettingsConfigDict(env_prefix="GOOGLE_")
    
    client_id: str = Field(default="", description="Google OAuth Client ID")
    client_secret: str = Field(default="", description="Google OAuth Client Secret")
    redirect_uri: str = Field(
        default="http://localhost:3000/api/auth/callback/google",
        description="OAuth redirect URI"
    )


class AppSettings(BaseSettings):
    """General application settings."""
    
    model_config = SettingsConfigDict(env_prefix="")
    
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        description="Comma-separated CORS origins"
    )
    rate_limit_per_minute: int = Field(
        default=100,
        description="Rate limit per minute per user"
    )
    jwt_algorithm: str = Field(default="RS256", description="JWT algorithm")


class Settings(BaseSettings):
    """Combined settings for the entire application."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    descope: DescopeSettings = Field(default_factory=DescopeSettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    google: GoogleSettings = Field(default_factory=GoogleSettings)
    app: AppSettings = Field(default_factory=AppSettings)
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.app.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export commonly used settings
settings = get_settings()
