"""FastAPI application entry point for Deep Research API."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deep_research_api.api.router import api_router
from deep_research_api.config import get_settings
from deep_research_api.services.database import close_db_service, init_db_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to the application.
    """
    # Startup
    await init_db_service()

    yield

    # Shutdown
    await close_db_service()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Deep Research Agent API - Multi-step iterative research with reasoning traces",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    return app


# Application instance
app = create_app()
