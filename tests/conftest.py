"""Shared test fixtures and configuration."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deep_research_api.dependencies import get_database_service
from deep_research_api.main import app
from deep_research_api.services.database import DatabaseService


@pytest.fixture
def mock_db_service() -> MagicMock:
    """Create a mock database service."""
    service = MagicMock(spec=DatabaseService)
    service.health_check = AsyncMock(
        return_value={"status": "healthy", "database": "connected", "pool_size": 5}
    )
    return service


@pytest.fixture
def mock_task() -> MagicMock:
    """Create a mock research task."""
    task = MagicMock()
    task.id = uuid4()
    task.query = "Test research query"
    task.config = {"max_iterations": 5, "depth": "standard"}
    task.status = "pending"
    task.result = None
    task.reasoning_trace = None
    task.error = None
    task.created_at = datetime.now(UTC)
    task.started_at = None
    task.completed_at = None
    task.metadata_ = {}
    return task


@pytest.fixture
def client(mock_db_service: MagicMock) -> TestClient:
    """Create a test client with mocked dependencies."""
    app.dependency_overrides[get_database_service] = lambda: mock_db_service
    yield TestClient(app)
    app.dependency_overrides.clear()
