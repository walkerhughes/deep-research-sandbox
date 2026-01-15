"""Tests for shared types package."""

from datetime import datetime

import pytest

from shared_types import (
    Citation,
    CreateResearchRequest,
    CreateResearchResponse,
    ErrorResponse,
    EventType,
    GetResearchResponse,
    HealthResponse,
    Inference,
    ReasoningStep,
    ResearchResult,
    ResearchTask,
    StepCompletedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskFailedEvent,
    TaskStartedEvent,
    TaskStatus,
)


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_status_values(self) -> None:
        """All expected status values exist."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"


class TestCitation:
    """Tests for Citation model."""

    def test_valid_citation(self) -> None:
        """Can create a valid citation."""
        citation = Citation(
            title="Test Article",
            url="https://example.com/article",
            snippet="This is a test snippet.",
        )
        assert citation.title == "Test Article"
        assert citation.url == "https://example.com/article"
        assert citation.snippet == "This is a test snippet."

    def test_citation_serialization(self) -> None:
        """Citation serializes to dict correctly."""
        citation = Citation(
            title="Test",
            url="https://example.com",
            snippet="snippet",
        )
        data = citation.model_dump()
        assert data == {
            "title": "Test",
            "url": "https://example.com",
            "snippet": "snippet",
        }


class TestInference:
    """Tests for Inference model."""

    def test_valid_inference(self) -> None:
        """Can create a valid inference."""
        inference = Inference(
            claim="Test claim",
            supporting_citations=["https://example.com"],
            degrees_of_separation=2,
            reasoning="Because of evidence X",
        )
        assert inference.claim == "Test claim"
        assert inference.degrees_of_separation == 2

    def test_inference_defaults(self) -> None:
        """Inference has correct defaults."""
        inference = Inference(
            claim="Test claim",
            reasoning="Test reasoning",
        )
        assert inference.supporting_citations == []
        assert inference.degrees_of_separation == 1

    def test_invalid_degrees_of_separation(self) -> None:
        """degrees_of_separation must be >= 1."""
        with pytest.raises(ValueError):
            Inference(
                claim="Test",
                reasoning="Test",
                degrees_of_separation=0,
            )


class TestReasoningStep:
    """Tests for ReasoningStep model."""

    def test_valid_step(self) -> None:
        """Can create a valid reasoning step."""
        step = ReasoningStep(
            step_number=1,
            action="search",
            input="quantum computing",
            output="Found 5 relevant articles",
            rationale="Need background information",
        )
        assert step.step_number == 1
        assert step.action == "search"


class TestResearchResult:
    """Tests for ResearchResult model."""

    def test_valid_result(self) -> None:
        """Can create a valid research result."""
        result = ResearchResult(
            summary="Test summary",
            key_findings=["Finding 1", "Finding 2"],
            inferences=[],
            reasoning_trace=[],
            citations=[],
            confidence_score=0.85,
        )
        assert result.summary == "Test summary"
        assert len(result.key_findings) == 2
        assert result.confidence_score == 0.85

    def test_confidence_score_bounds(self) -> None:
        """confidence_score must be between 0 and 1."""
        with pytest.raises(ValueError):
            ResearchResult(
                summary="Test",
                confidence_score=1.5,
            )
        with pytest.raises(ValueError):
            ResearchResult(
                summary="Test",
                confidence_score=-0.1,
            )


class TestResearchTask:
    """Tests for ResearchTask model."""

    def test_valid_task(self) -> None:
        """Can create a valid research task."""
        task = ResearchTask(
            id="task-123",
            query="What is quantum computing?",
        )
        assert task.id == "task-123"
        assert task.status == TaskStatus.PENDING
        assert task.result is None

    def test_task_with_result(self) -> None:
        """Can create a completed task with result."""
        result = ResearchResult(
            summary="Quantum computing uses qubits",
            confidence_score=0.9,
        )
        task = ResearchTask(
            id="task-123",
            query="What is quantum computing?",
            status=TaskStatus.COMPLETED,
            result=result,
            completed_at=datetime.utcnow(),
        )
        assert task.status == TaskStatus.COMPLETED
        assert task.result is not None
        assert task.result.summary == "Quantum computing uses qubits"


class TestEvents:
    """Tests for event models."""

    def test_task_created_event(self) -> None:
        """Can create TaskCreatedEvent."""
        event = TaskCreatedEvent(
            task_id="task-123",
            query="Test query",
        )
        assert event.event_type == EventType.TASK_CREATED
        assert event.query == "Test query"

    def test_task_started_event(self) -> None:
        """Can create TaskStartedEvent."""
        event = TaskStartedEvent(task_id="task-123")
        assert event.event_type == EventType.TASK_STARTED

    def test_step_completed_event(self) -> None:
        """Can create StepCompletedEvent."""
        step = ReasoningStep(
            step_number=1,
            action="search",
            input="test",
            output="results",
            rationale="needed info",
        )
        event = StepCompletedEvent(task_id="task-123", step=step)
        assert event.event_type == EventType.STEP_COMPLETED
        assert event.step.step_number == 1

    def test_task_completed_event(self) -> None:
        """Can create TaskCompletedEvent."""
        result = ResearchResult(summary="Done", confidence_score=0.9)
        event = TaskCompletedEvent(task_id="task-123", result=result)
        assert event.event_type == EventType.TASK_COMPLETED

    def test_task_failed_event(self) -> None:
        """Can create TaskFailedEvent."""
        event = TaskFailedEvent(
            task_id="task-123",
            error="Something went wrong",
        )
        assert event.event_type == EventType.TASK_FAILED
        assert event.error == "Something went wrong"


class TestAPIModels:
    """Tests for API request/response models."""

    def test_create_research_request(self) -> None:
        """Can create valid request."""
        request = CreateResearchRequest(query="Test query")
        assert request.query == "Test query"
        assert request.webhook_url is None
        assert request.max_iterations == 5

    def test_create_research_request_validation(self) -> None:
        """Request validates query length."""
        with pytest.raises(ValueError):
            CreateResearchRequest(query="")

    def test_create_research_response(self) -> None:
        """Can create valid response."""
        response = CreateResearchResponse(
            task_id="task-123",
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        assert response.task_id == "task-123"

    def test_error_response(self) -> None:
        """Can create error response."""
        error = ErrorResponse(
            error="not_found",
            message="Task not found",
        )
        assert error.error == "not_found"

    def test_health_response(self) -> None:
        """Can create health response."""
        health = HealthResponse(
            status="healthy",
            version="0.1.0",
        )
        assert health.status == "healthy"
