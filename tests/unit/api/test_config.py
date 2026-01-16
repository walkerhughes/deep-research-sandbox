"""Unit tests for configuration module."""

from deep_research_api.config import Settings, get_settings


def test_settings_defaults() -> None:
    """Test that settings have sensible defaults."""
    settings = Settings()

    assert settings.app_name == "Deep Research API"
    assert settings.app_version == "0.1.0"
    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000


def test_settings_cors_defaults() -> None:
    """Test CORS settings defaults."""
    settings = Settings()

    assert "http://localhost:3000" in settings.cors_origins
    assert "http://localhost:8000" in settings.cors_origins
    assert settings.cors_allow_credentials is True


def test_settings_database_url_fallback() -> None:
    """Test database URL fallback for local development."""
    settings = Settings(supabase_db_host="")

    assert (
        settings.database_url
        == "postgresql+asyncpg://postgres:postgres@localhost:5432/deep_research"
    )


def test_settings_database_url_with_supabase() -> None:
    """Test database URL construction with Supabase settings."""
    settings = Settings(
        supabase_db_host="db.example.supabase.co",
        supabase_db_port=5432,
        supabase_db_name="postgres",
        supabase_db_user="postgres",
        supabase_db_password="secret",
    )

    expected = "postgresql+asyncpg://postgres:secret@db.example.supabase.co:5432/postgres"
    assert settings.database_url == expected


def test_get_settings_cached() -> None:
    """Test that get_settings returns cached instance."""
    # Clear cache first
    get_settings.cache_clear()

    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2
