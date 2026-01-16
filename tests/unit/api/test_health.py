"""Unit tests for health check endpoints."""

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient


def test_health_check_healthy(client: TestClient, mock_db_service: MagicMock) -> None:
    """Test health check returns healthy when database is connected."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["api"] == "ok"
    assert data["database"]["status"] == "healthy"


def test_health_check_degraded(client: TestClient, mock_db_service: MagicMock) -> None:
    """Test health check returns degraded when database is unhealthy."""
    mock_db_service.health_check = AsyncMock(
        return_value={
            "status": "unhealthy",
            "database": "disconnected",
            "error": "Connection failed",
        }
    )

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["database"]["status"] == "unhealthy"


def test_liveness_check(client: TestClient) -> None:
    """Test liveness probe returns alive."""
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_readiness_check_ready(client: TestClient, mock_db_service: MagicMock) -> None:
    """Test readiness probe returns ready when all checks pass."""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"] == "healthy"


def test_readiness_check_not_ready(client: TestClient, mock_db_service: MagicMock) -> None:
    """Test readiness probe returns not_ready when database is down."""
    mock_db_service.health_check = AsyncMock(
        return_value={"status": "unhealthy", "database": "disconnected"}
    )

    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_ready"
