"""Unit tests for research endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_research_task(
    client: TestClient, mock_db_service: MagicMock, mock_task: MagicMock
) -> None:
    """Test creating a new research task."""
    mock_db_service.create_task = AsyncMock(return_value=mock_task)

    response = client.post(
        "/research",
        json={
            "query": "What is quantum computing?",
            "config": {"max_iterations": 5, "depth": "thorough"},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["task_id"] == str(mock_task.id)
    assert data["status"] == "pending"
    assert "created_at" in data

    mock_db_service.create_task.assert_called_once()


def test_create_research_task_default_config(
    client: TestClient, mock_db_service: MagicMock, mock_task: MagicMock
) -> None:
    """Test creating a research task with default config."""
    mock_db_service.create_task = AsyncMock(return_value=mock_task)

    response = client.post("/research", json={"query": "Simple query"})

    assert response.status_code == 201
    mock_db_service.create_task.assert_called_once()


def test_create_research_task_invalid_query(client: TestClient) -> None:
    """Test creating a research task with empty query."""
    response = client.post("/research", json={"query": ""})

    assert response.status_code == 422  # Validation error


def test_get_research_task(
    client: TestClient, mock_db_service: MagicMock, mock_task: MagicMock
) -> None:
    """Test getting a research task by ID."""
    mock_db_service.get_task = AsyncMock(return_value=mock_task)

    response = client.get(f"/research/{mock_task.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == str(mock_task.id)
    assert data["status"] == "pending"

    mock_db_service.get_task.assert_called_once_with(mock_task.id)


def test_get_research_task_completed(
    client: TestClient, mock_db_service: MagicMock, mock_task: MagicMock
) -> None:
    """Test getting a completed research task with results."""
    mock_task.status = "completed"
    mock_task.result = {
        "summary": "Quantum computing uses quantum mechanics for computation.",
        "findings": [{"text": "Finding 1"}],
        "citations": [{"url": "https://example.com", "title": "Source"}],
    }
    mock_task.reasoning_trace = {"steps": []}
    mock_task.completed_at = datetime.now(UTC)

    mock_db_service.get_task = AsyncMock(return_value=mock_task)

    response = client.get(f"/research/{mock_task.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["result"]["summary"] == "Quantum computing uses quantum mechanics for computation."


def test_get_research_task_not_found(client: TestClient, mock_db_service: MagicMock) -> None:
    """Test getting a non-existent research task."""
    mock_db_service.get_task = AsyncMock(return_value=None)

    task_id = uuid4()
    response = client.get(f"/research/{task_id}")

    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_stream_research_task_not_found(client: TestClient, mock_db_service: MagicMock) -> None:
    """Test streaming a non-existent research task."""
    mock_db_service.get_task = AsyncMock(return_value=None)

    task_id = uuid4()
    response = client.get(f"/research/{task_id}/stream")

    assert response.status_code == 404
