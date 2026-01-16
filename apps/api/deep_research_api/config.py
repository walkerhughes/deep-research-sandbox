"""Application configuration settings for Deep Research API."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="Deep Research API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Deployment environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")

    # Database settings (Supabase)
    supabase_url: str = Field(default="", description="Supabase project URL")
    supabase_anon_key: str = Field(default="", description="Supabase anonymous key")
    supabase_service_key: str = Field(default="", description="Supabase service role key")
    supabase_db_host: str = Field(default="", description="Supabase database host")
    supabase_db_port: int = Field(default=5432, description="Database port")
    supabase_db_name: str = Field(default="postgres", description="Database name")
    supabase_db_user: str = Field(default="postgres", description="Database user")
    supabase_db_password: str = Field(default="", description="Database password")

    # Connection pool settings
    db_pool_size: int = Field(default=5, description="Database connection pool size")
    db_max_overflow: int = Field(default=10, description="Max overflow connections")

    # API Keys
    openai_api_key: str = Field(default="", description="OpenAI API key")
    perplexity_api_key: str = Field(default="", description="Perplexity API key")

    # Webhook settings
    webhook_secret: str = Field(default="", description="Webhook signature secret")
    frontend_webhook_url: str = Field(default="", description="Frontend webhook URL")

    # Observability
    langsmith_api_key: str = Field(default="", description="LangSmith API key")
    otel_exporter_otlp_endpoint: str = Field(
        default="", description="OpenTelemetry OTLP exporter endpoint"
    )

    @property
    def database_url(self) -> str:
        """Build the async database URL for SQLAlchemy."""
        if self.supabase_db_host:
            return (
                f"postgresql+asyncpg://{self.supabase_db_user}:{self.supabase_db_password}"
                f"@{self.supabase_db_host}:{self.supabase_db_port}/{self.supabase_db_name}"
            )
        # Fallback for local development
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/deep_research"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        The Settings singleton instance.
    """
    return Settings()
