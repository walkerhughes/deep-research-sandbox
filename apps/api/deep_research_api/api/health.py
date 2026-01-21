"""Health check endpoints."""

from typing import Any

from fastapi import APIRouter, Depends

from deep_research_api.dependencies import get_database_service
from deep_research_api.services.database import DatabaseService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db_service: DatabaseService = Depends(get_database_service),
) -> dict[str, Any]:
    """Check API and database health.

    Returns:
        Health status including database connectivity.
    """
    db_health = await db_service.health_check()

    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "api": "ok",
        "database": db_health,
    }


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    """Simple liveness probe for container orchestration.

    Returns:
        Simple status indicating the API is alive.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_check(
    db_service: DatabaseService = Depends(get_database_service),
) -> dict[str, Any]:
    """Readiness probe checking all dependencies.

    Returns:
        Status indicating if the API is ready to serve traffic.
    """
    db_health = await db_service.health_check()

    is_ready = db_health["status"] == "healthy"

    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": {
            "database": db_health["status"],
        },
    }
