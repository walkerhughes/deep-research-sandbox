"""Webhook and stream event models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from shared_types.research import ReasoningStep, ResearchResult, TaskStatus


class EventType(str, Enum):
    """Types of events that can be emitted."""

    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    STEP_COMPLETED = "step_completed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"


class BaseEvent(BaseModel):
    """Base model for all events."""

    event_type: EventType = Field(..., description="Type of event")
    task_id: str = Field(..., description="ID of the associated task")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")


class TaskCreatedEvent(BaseEvent):
    """Event emitted when a task is created."""

    event_type: EventType = Field(default=EventType.TASK_CREATED, frozen=True)
    query: str = Field(..., description="Research query")


class TaskStartedEvent(BaseEvent):
    """Event emitted when task execution begins."""

    event_type: EventType = Field(default=EventType.TASK_STARTED, frozen=True)


class StepCompletedEvent(BaseEvent):
    """Event emitted when a reasoning step completes."""

    event_type: EventType = Field(default=EventType.STEP_COMPLETED, frozen=True)
    step: ReasoningStep = Field(..., description="The completed reasoning step")


class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task completes successfully."""

    event_type: EventType = Field(default=EventType.TASK_COMPLETED, frozen=True)
    result: ResearchResult = Field(..., description="Final research result")


class TaskFailedEvent(BaseEvent):
    """Event emitted when a task fails."""

    event_type: EventType = Field(default=EventType.TASK_FAILED, frozen=True)
    error: str = Field(..., description="Error message")
    error_details: dict[str, Any] | None = Field(default=None, description="Additional error info")


# Union type for all events
StreamEvent = (
    TaskCreatedEvent
    | TaskStartedEvent
    | StepCompletedEvent
    | TaskCompletedEvent
    | TaskFailedEvent
)
