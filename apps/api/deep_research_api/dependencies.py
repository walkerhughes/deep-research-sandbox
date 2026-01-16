"""FastAPI dependency injection providers."""

from typing import Annotated

from fastapi import Depends

from deep_research_api.config import Settings, get_settings
from deep_research_api.services.database import DatabaseService, get_db_service


def get_database_service() -> DatabaseService:
    """Get the database service dependency.

    Returns:
        The DatabaseService singleton instance.
    """
    return get_db_service()


# Type aliases for cleaner dependency injection in routes
SettingsDep = Annotated[Settings, Depends(get_settings)]
DatabaseDep = Annotated[DatabaseService, Depends(get_database_service)]
