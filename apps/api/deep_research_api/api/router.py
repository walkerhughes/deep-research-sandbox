"""Main API router combining all route modules."""

from fastapi import APIRouter

from deep_research_api.api.health import router as health_router
from deep_research_api.api.research import router as research_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(health_router)
api_router.include_router(research_router)
