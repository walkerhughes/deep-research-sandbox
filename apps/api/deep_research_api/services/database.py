"""Database service for Deep Research Agent.

Provides async database operations with connection pooling for Supabase PostgreSQL.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from deep_research_api.models.database import (
    Base,
    EvalResult,
    Inference,
    ResearchFinding,
    ResearchTask,
    TaskStatus,
)


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    supabase_url: str = Field(default="", description="Supabase project URL")
    supabase_db_host: str = Field(default="", description="Supabase database host")
    supabase_db_port: int = Field(default=5432, description="Database port")
    supabase_db_name: str = Field(default="postgres", description="Database name")
    supabase_db_user: str = Field(default="postgres", description="Database user")
    supabase_db_password: str = Field(default="", description="Database password")

    # Connection pool settings
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Max overflow connections")
    pool_timeout: int = Field(default=30, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=1800, description="Connection recycle time in seconds")

    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}

    @property
    def database_url(self) -> str:
        """Build the async database URL for SQLAlchemy."""
        if self.supabase_db_host:
            return (
                f"postgresql+asyncpg://{self.supabase_db_user}:{self.supabase_db_password}"
                f"@{self.supabase_db_host}:{self.supabase_db_port}/{self.supabase_db_name}"
            )
        # Fallback for local development
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/deep_research"


class TaskCreate(BaseModel):
    """Schema for creating a new research task."""

    query: str
    config: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: UUID
    query: str
    config: dict[str, Any]
    status: str
    result: dict[str, Any] | None
    reasoning_trace: dict[str, Any] | None
    error: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    metadata: dict[str, Any]

    model_config = {"from_attributes": True}


class FindingCreate(BaseModel):
    """Schema for creating a research finding."""

    sub_query: str
    response: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float | None = None


class InferenceCreate(BaseModel):
    """Schema for creating an inference."""

    claim: str
    supporting_citations: list[dict[str, Any]] = Field(default_factory=list)
    degrees_of_separation: int
    reasoning: str


class EvalResultCreate(BaseModel):
    """Schema for creating an eval result."""

    eval_type: str
    score: float | None = None
    details: dict[str, Any] | None = None


class DatabaseService:
    """Async database service with connection pooling."""

    def __init__(self, settings: DatabaseSettings | None = None):
        """Initialize the database service.

        Args:
            settings: Database configuration settings. If None, loads from environment.
        """
        self.settings = settings or DatabaseSettings()
        self._engine = create_async_engine(
            self.settings.database_url,
            pool_size=self.settings.pool_size,
            max_overflow=self.settings.max_overflow,
            pool_timeout=self.settings.pool_timeout,
            pool_recycle=self.settings.pool_recycle,
            echo=False,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def init_db(self) -> None:
        """Initialize database tables (for development/testing)."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Close database connections."""
        await self._engine.dispose()

    async def health_check(self) -> dict[str, Any]:
        """Check database connectivity.

        Returns:
            Health status with connection info.
        """
        try:
            async with self._session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                return {
                    "status": "healthy",
                    "database": "connected",
                    "pool_size": self.settings.pool_size,
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            }

    # Task operations

    async def create_task(
        self,
        query: str,
        config: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ResearchTask:
        """Create a new research task.

        Args:
            query: The research query.
            config: Optional task configuration.
            metadata: Optional task metadata.

        Returns:
            The created ResearchTask.
        """
        async with self._session_factory() as session:
            task = ResearchTask(
                query=query,
                config=config or {},
                metadata_=metadata or {},
                status=TaskStatus.PENDING.value,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    async def get_task(self, task_id: UUID) -> ResearchTask | None:
        """Get a research task by ID.

        Args:
            task_id: The task UUID.

        Returns:
            The ResearchTask if found, None otherwise.
        """
        async with self._session_factory() as session:
            result = await session.execute(select(ResearchTask).where(ResearchTask.id == task_id))
            return result.scalar_one_or_none()

    async def list_tasks(
        self,
        limit: int = 20,
        offset: int = 0,
        status: TaskStatus | None = None,
    ) -> list[ResearchTask]:
        """List research tasks with pagination.

        Args:
            limit: Maximum number of tasks to return.
            offset: Number of tasks to skip.
            status: Optional status filter.

        Returns:
            List of ResearchTask objects.
        """
        async with self._session_factory() as session:
            query = select(ResearchTask).order_by(ResearchTask.created_at.desc())
            if status:
                query = query.where(ResearchTask.status == status.value)
            query = query.limit(limit).offset(offset)
            result = await session.execute(query)
            return list(result.scalars().all())

    async def update_task_status(
        self,
        task_id: UUID,
        status: TaskStatus,
        error: str | None = None,
    ) -> ResearchTask | None:
        """Update the status of a research task.

        Args:
            task_id: The task UUID.
            status: The new status.
            error: Optional error message (for failed status).

        Returns:
            The updated ResearchTask if found, None otherwise.
        """
        async with self._session_factory() as session:
            result = await session.execute(select(ResearchTask).where(ResearchTask.id == task_id))
            task = result.scalar_one_or_none()
            if not task:
                return None

            task.status = status.value
            now = datetime.now(UTC)

            if status == TaskStatus.RUNNING and task.started_at is None:
                task.started_at = now
            elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                task.completed_at = now
                if error:
                    task.error = error

            await session.commit()
            await session.refresh(task)
            return task

    async def save_result(
        self,
        task_id: UUID,
        result: dict[str, Any],
        reasoning_trace: dict[str, Any] | None = None,
    ) -> ResearchTask | None:
        """Save the result of a research task.

        Args:
            task_id: The task UUID.
            result: The research result.
            reasoning_trace: Optional reasoning trace.

        Returns:
            The updated ResearchTask if found, None otherwise.
        """
        async with self._session_factory() as session:
            query_result = await session.execute(
                select(ResearchTask).where(ResearchTask.id == task_id)
            )
            task = query_result.scalar_one_or_none()
            if not task:
                return None

            task.result = result
            if reasoning_trace:
                task.reasoning_trace = reasoning_trace
            task.status = TaskStatus.COMPLETED.value
            task.completed_at = datetime.now(UTC)

            await session.commit()
            await session.refresh(task)
            return task

    # Finding operations

    async def add_finding(
        self,
        task_id: UUID,
        sub_query: str,
        response: str,
        citations: list[dict[str, Any]] | None = None,
        confidence: float | None = None,
    ) -> ResearchFinding:
        """Add a research finding to a task.

        Args:
            task_id: The task UUID.
            sub_query: The sub-query that produced this finding.
            response: The finding response.
            citations: Optional list of citations.
            confidence: Optional confidence score (0.0 to 1.0).

        Returns:
            The created ResearchFinding.
        """
        async with self._session_factory() as session:
            finding = ResearchFinding(
                task_id=task_id,
                sub_query=sub_query,
                response=response,
                citations=citations or [],
                confidence=confidence,
            )
            session.add(finding)
            await session.commit()
            await session.refresh(finding)
            return finding

    async def get_findings(self, task_id: UUID) -> list[ResearchFinding]:
        """Get all findings for a task.

        Args:
            task_id: The task UUID.

        Returns:
            List of ResearchFinding objects.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(ResearchFinding)
                .where(ResearchFinding.task_id == task_id)
                .order_by(ResearchFinding.created_at)
            )
            return list(result.scalars().all())

    # Inference operations

    async def add_inference(
        self,
        task_id: UUID,
        claim: str,
        degrees_of_separation: int,
        reasoning: str,
        supporting_citations: list[dict[str, Any]] | None = None,
    ) -> Inference:
        """Add an inference to a task.

        Args:
            task_id: The task UUID.
            claim: The inference claim.
            degrees_of_separation: Number of inference steps from source data.
            reasoning: The reasoning behind the inference.
            supporting_citations: Optional list of supporting citations.

        Returns:
            The created Inference.
        """
        async with self._session_factory() as session:
            inference = Inference(
                task_id=task_id,
                claim=claim,
                degrees_of_separation=degrees_of_separation,
                reasoning=reasoning,
                supporting_citations=supporting_citations or [],
            )
            session.add(inference)
            await session.commit()
            await session.refresh(inference)
            return inference

    async def get_inferences(self, task_id: UUID) -> list[Inference]:
        """Get all inferences for a task.

        Args:
            task_id: The task UUID.

        Returns:
            List of Inference objects.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(Inference).where(Inference.task_id == task_id).order_by(Inference.created_at)
            )
            return list(result.scalars().all())

    # Eval result operations

    async def add_eval_result(
        self,
        task_id: UUID,
        eval_type: str,
        score: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Add an evaluation result to a task.

        Args:
            task_id: The task UUID.
            eval_type: The type of evaluation.
            score: Optional evaluation score (0.0 to 1.0).
            details: Optional evaluation details.

        Returns:
            The created EvalResult.
        """
        async with self._session_factory() as session:
            eval_result = EvalResult(
                task_id=task_id,
                eval_type=eval_type,
                score=score,
                details=details,
            )
            session.add(eval_result)
            await session.commit()
            await session.refresh(eval_result)
            return eval_result

    async def get_eval_results(self, task_id: UUID) -> list[EvalResult]:
        """Get all eval results for a task.

        Args:
            task_id: The task UUID.

        Returns:
            List of EvalResult objects.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(EvalResult)
                .where(EvalResult.task_id == task_id)
                .order_by(EvalResult.created_at)
            )
            return list(result.scalars().all())


# Global database service instance
_db_service: DatabaseService | None = None


def get_db_service() -> DatabaseService:
    """Get the global database service instance.

    Returns:
        The DatabaseService singleton.
    """
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service


async def init_db_service() -> DatabaseService:
    """Initialize and return the database service.

    Returns:
        The initialized DatabaseService.
    """
    service = get_db_service()
    return service


async def close_db_service() -> None:
    """Close the database service."""
    global _db_service
    if _db_service is not None:
        await _db_service.close()
        _db_service = None
