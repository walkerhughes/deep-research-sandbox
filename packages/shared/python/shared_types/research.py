"""Research-related Pydantic models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of a research task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Citation(BaseModel):
    """A citation from a research source."""

    title: str = Field(..., description="Title of the source")
    url: str = Field(..., description="URL of the source")
    snippet: str = Field(..., description="Relevant excerpt from the source")


class Inference(BaseModel):
    """An inference derived from research findings."""

    claim: str = Field(..., description="The inference or claim being made")
    supporting_citations: list[str] = Field(
        default_factory=list,
        description="IDs or URLs of citations supporting this inference",
    )
    degrees_of_separation: int = Field(
        default=1,
        ge=1,
        description="How many logical steps from direct evidence",
    )
    reasoning: str = Field(..., description="Explanation of the reasoning chain")


class ReasoningStep(BaseModel):
    """A step in the research agent's reasoning trace."""

    step_number: int = Field(..., ge=1, description="Sequential step number")
    action: str = Field(..., description="Action taken (e.g., 'search', 'analyze', 'synthesize')")
    input: str = Field(..., description="Input to this step")
    output: str = Field(..., description="Output from this step")
    rationale: str = Field(..., description="Why this action was taken")


class ResearchResult(BaseModel):
    """Complete result of a research task."""

    summary: str = Field(..., description="Executive summary of findings")
    key_findings: list[str] = Field(
        default_factory=list,
        description="Bullet-point key findings",
    )
    inferences: list[Inference] = Field(
        default_factory=list,
        description="Inferences derived from research",
    )
    reasoning_trace: list[ReasoningStep] = Field(
        default_factory=list,
        description="Step-by-step reasoning trace",
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="All citations used in research",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the results (0-1)",
    )


class ResearchTask(BaseModel):
    """A research task with its status and results."""

    id: str = Field(..., description="Unique task identifier")
    query: str = Field(..., description="Original research query")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    result: ResearchResult | None = Field(default=None, description="Research result if completed")
    error_message: str | None = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation time")
    started_at: datetime | None = Field(default=None, description="When task started running")
    completed_at: datetime | None = Field(default=None, description="Task completion time")
