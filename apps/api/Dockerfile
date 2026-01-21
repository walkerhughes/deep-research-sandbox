# Deep Research API Dockerfile
# For local development and production deployment

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Development stage
FROM base AS development

# Copy workspace files
COPY pyproject.toml uv.lock* ./
COPY packages/shared/python ./packages/shared/python/
COPY apps/api ./apps/api/

# Install dependencies
RUN uv sync --frozen --no-dev || uv sync

# Set working directory to api
WORKDIR /app/apps/api

# Expose port
EXPOSE 8000

# Run with hot reload for development
CMD ["uv", "run", "uvicorn", "deep_research_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

# Copy workspace files
COPY pyproject.toml uv.lock* ./
COPY packages/shared/python ./packages/shared/python/
COPY apps/api ./apps/api/

# Install dependencies (production only)
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Set working directory to api
WORKDIR /app/apps/api

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Run production server
CMD ["uv", "run", "uvicorn", "deep_research_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
