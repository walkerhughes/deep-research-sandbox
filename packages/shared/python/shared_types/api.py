"""API request and response models."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from shared_types.research import ResearchResult, ResearchTask, TaskStatus


class CreateResearchRequest(BaseModel):
    """Request to create a new research task."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Research query to investigate",
    )
    webhook_url: str | None = Field(
        default=None,
        description="URL to receive webhook notifications",
    )
    max_iterations: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum research iterations",
    )


class CreateResearchResponse(BaseModel):
    """Response after creating a research task."""

    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Initial task status")
    created_at: datetime = Field(..., description="Task creation timestamp")


class GetResearchResponse(BaseModel):
    """Response when retrieving a research task."""

    task: ResearchTask = Field(..., description="The research task")


class ResearchStreamChunk(BaseModel):
    """A chunk in the research SSE stream."""

    event: Literal[
        "task_created",
        "task_started",
        "step_completed",
        "task_completed",
        "task_failed",
        "heartbeat",
    ] = Field(..., description="Event type")
    data: dict[str, Any] = Field(..., description="Event payload")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ..., description="Service health status"
    )
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
