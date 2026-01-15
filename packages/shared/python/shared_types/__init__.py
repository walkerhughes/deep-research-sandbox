"""Deep Research Shared Types - Common types for API contracts."""

from shared_types.research import (
    Citation,
    Inference,
    ReasoningStep,
    ResearchResult,
    ResearchTask,
    TaskStatus,
)
from shared_types.events import (
    EventType,
    BaseEvent,
    TaskCreatedEvent,
    TaskStartedEvent,
    StepCompletedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
    StreamEvent,
)
from shared_types.api import (
    CreateResearchRequest,
    CreateResearchResponse,
    GetResearchResponse,
    ResearchStreamChunk,
    ErrorResponse,
    HealthResponse,
)

__all__ = [
    # Research models
    "Citation",
    "Inference",
    "ReasoningStep",
    "ResearchResult",
    "ResearchTask",
    "TaskStatus",
    # Event models
    "EventType",
    "BaseEvent",
    "TaskCreatedEvent",
    "TaskStartedEvent",
    "StepCompletedEvent",
    "TaskCompletedEvent",
    "TaskFailedEvent",
    "StreamEvent",
    # API models
    "CreateResearchRequest",
    "CreateResearchResponse",
    "GetResearchResponse",
    "ResearchStreamChunk",
    "ErrorResponse",
    "HealthResponse",
]
