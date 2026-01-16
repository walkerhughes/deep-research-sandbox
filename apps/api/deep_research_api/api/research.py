"""Research task endpoints."""

import asyncio
import json
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from deep_research_api.dependencies import get_database_service
from deep_research_api.models.research import (
    ResearchCreateResponse,
    ResearchRequest,
    ResearchResponse,
    ResearchResult,
    StreamEvent,
    TaskStatus,
)
from deep_research_api.services.database import DatabaseService

router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_research_task(
    request: ResearchRequest,
    db_service: DatabaseService = Depends(get_database_service),
) -> ResearchCreateResponse:
    """Create a new research task.

    Args:
        request: The research request containing query and configuration.
        db_service: Injected database service.

    Returns:
        The created task with ID and status.
    """
    task = await db_service.create_task(
        query=request.query,
        config=request.config.model_dump(),
    )

    return ResearchCreateResponse(
        task_id=task.id,
        status=TaskStatus.PENDING,
        created_at=task.created_at,
    )


@router.get("/{task_id}", response_model=ResearchResponse)
async def get_research_task(
    task_id: UUID,
    db_service: DatabaseService = Depends(get_database_service),
) -> ResearchResponse:
    """Get a research task by ID.

    Args:
        task_id: The task UUID.
        db_service: Injected database service.

    Returns:
        The full research task details.

    Raises:
        HTTPException: If task not found.
    """
    task = await db_service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research task {task_id} not found",
        )

    # Convert task to response
    result = None
    if task.result:
        result = ResearchResult(
            summary=task.result.get("summary", ""),
            findings=task.result.get("findings", []),
            citations=task.result.get("citations", []),
        )

    reasoning_trace = []
    if task.reasoning_trace:
        reasoning_trace = task.reasoning_trace.get("steps", [])

    return ResearchResponse(
        task_id=task.id,
        status=TaskStatus(task.status),
        result=result,
        reasoning_trace=reasoning_trace,
        error=task.error,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


async def _generate_stream_events(
    task_id: UUID,
    db_service: DatabaseService,
) -> Any:
    """Generate SSE events for a research task.

    Args:
        task_id: The task UUID to stream.
        db_service: Database service for fetching task updates.

    Yields:
        SSE events with task progress updates.
    """
    last_status = None

    while True:
        task = await db_service.get_task(task_id)

        if not task:
            yield {
                "event": "error",
                "data": json.dumps({"error": f"Task {task_id} not found"}),
            }
            break

        current_status = task.status

        # Send status update if changed
        if current_status != last_status:
            event = StreamEvent(
                event="status",
                data={"status": current_status, "task_id": str(task_id)},
            )
            yield {"event": event.event, "data": json.dumps(event.data)}
            last_status = current_status

        # Check for completion or failure
        if current_status == TaskStatus.COMPLETED.value:
            result_data = {
                "task_id": str(task_id),
                "result": task.result,
                "reasoning_trace": task.reasoning_trace,
            }
            yield {"event": "complete", "data": json.dumps(result_data)}
            break
        elif current_status == TaskStatus.FAILED.value:
            yield {
                "event": "error",
                "data": json.dumps({"error": task.error or "Task failed"}),
            }
            break

        # Poll interval
        await asyncio.sleep(1.0)


@router.get("/{task_id}/stream")
async def stream_research_task(
    task_id: UUID,
    db_service: DatabaseService = Depends(get_database_service),
) -> EventSourceResponse:
    """Stream research task progress via Server-Sent Events.

    Args:
        task_id: The task UUID to stream.
        db_service: Injected database service.

    Returns:
        SSE stream of task progress updates.

    Raises:
        HTTPException: If task not found.
    """
    # Verify task exists before starting stream
    task = await db_service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research task {task_id} not found",
        )

    return EventSourceResponse(_generate_stream_events(task_id, db_service))
