"""Pydantic models for research API request/response schemas."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ResearchDepth(str, Enum):
    """Research depth levels."""

    QUICK = "quick"
    STANDARD = "standard"
    THOROUGH = "thorough"


class TaskStatus(str, Enum):
    """Status values for research tasks."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchConfig(BaseModel):
    """Configuration options for a research task."""

    max_iterations: int = Field(default=5, ge=1, le=20, description="Maximum research iterations")
    depth: ResearchDepth = Field(default=ResearchDepth.STANDARD, description="Research depth level")


class ResearchRequest(BaseModel):
    """Request schema for creating a research task."""

    query: str = Field(..., min_length=1, max_length=5000, description="The research query")
    config: ResearchConfig = Field(
        default_factory=ResearchConfig, description="Research configuration"
    )


class ResearchCreateResponse(BaseModel):
    """Response schema for research task creation."""

    task_id: UUID = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    created_at: datetime = Field(..., description="Task creation timestamp")


class Citation(BaseModel):
    """A citation/source reference."""

    url: str = Field(..., description="Source URL")
    title: str = Field(default="", description="Source title")
    snippet: str = Field(default="", description="Relevant snippet from source")


class ReasoningStep(BaseModel):
    """A single step in the reasoning trace."""

    step: int = Field(..., description="Step number")
    action: str = Field(..., description="Action taken (e.g., 'search', 'analyze', 'synthesize')")
    description: str = Field(..., description="Description of what was done")
    timestamp: datetime = Field(..., description="When this step occurred")


class ResearchResult(BaseModel):
    """The result of a completed research task."""

    summary: str = Field(..., description="Summary of research findings")
    findings: list[dict[str, Any]] = Field(default_factory=list, description="Detailed findings")
    citations: list[Citation] = Field(default_factory=list, description="Source citations")


class ResearchResponse(BaseModel):
    """Full response schema for a research task."""

    task_id: UUID = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    result: ResearchResult | None = Field(default=None, description="Research result if completed")
    reasoning_trace: list[ReasoningStep] = Field(
        default_factory=list, description="Steps taken during research"
    )
    error: str | None = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(..., description="Task creation timestamp")
    completed_at: datetime | None = Field(default=None, description="Task completion timestamp")


class StreamEvent(BaseModel):
    """Server-sent event for research progress streaming."""

    event: str = Field(..., description="Event type (e.g., 'progress', 'finding', 'complete')")
    data: dict[str, Any] = Field(..., description="Event data payload")
