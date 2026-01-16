"""SQLAlchemy models for Deep Research Agent database schema."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID as PyUUID
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class TaskStatus(str, Enum):
    """Status values for research tasks."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvalType(str, Enum):
    """Types of evaluations that can be run on research tasks."""

    REASONING_QUALITY = "reasoning_quality"
    HALLUCINATION = "hallucination"
    CITATION_ACCURACY = "citation_accuracy"
    INFERENCE_VALIDITY = "inference_validity"
    SOURCE_RELEVANCE = "source_relevance"
    COMPLETENESS = "completeness"


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class ResearchTask(Base):
    """Model for research tasks.

    Stores the main research queries and their execution state.
    """

    __tablename__ = "research_tasks"

    id: Mapped[PyUUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String, nullable=False, default=TaskStatus.PENDING.value)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    reasoning_trace: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    findings: Mapped[list["ResearchFinding"]] = relationship(
        "ResearchFinding", back_populates="task", cascade="all, delete-orphan"
    )
    inferences: Mapped[list["Inference"]] = relationship(
        "Inference", back_populates="task", cascade="all, delete-orphan"
    )
    eval_results: Mapped[list["EvalResult"]] = relationship(
        "EvalResult", back_populates="task", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="chk_task_status",
        ),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_created", created_at.desc()),
        Index("idx_tasks_status_created", "status", created_at.desc()),
    )


class ResearchFinding(Base):
    """Model for research findings.

    Stores individual findings from sub-queries during research.
    """

    __tablename__ = "research_findings"

    id: Mapped[PyUUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id: Mapped[PyUUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False
    )
    sub_query: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task: Mapped["ResearchTask"] = relationship("ResearchTask", back_populates="findings")

    __table_args__ = (
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)",
            name="chk_confidence_range",
        ),
        Index("idx_findings_task", "task_id"),
        Index("idx_findings_task_created", "task_id", "created_at"),
    )


class Inference(Base):
    """Model for inferences.

    Tracks reasoning steps and inferences made during research for eval tracking.
    """

    __tablename__ = "inferences"

    id: Mapped[PyUUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id: Mapped[PyUUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False
    )
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    degrees_of_separation: Mapped[int] = mapped_column(Integer, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task: Mapped["ResearchTask"] = relationship("ResearchTask", back_populates="inferences")

    __table_args__ = (
        CheckConstraint(
            "degrees_of_separation >= 0",
            name="chk_degrees_non_negative",
        ),
        Index("idx_inferences_task", "task_id"),
        Index("idx_inferences_degrees", "degrees_of_separation"),
    )


class EvalResult(Base):
    """Model for evaluation results.

    Stores evaluation scores for research quality metrics.
    """

    __tablename__ = "eval_results"

    id: Mapped[PyUUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id: Mapped[PyUUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False
    )
    eval_type: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task: Mapped["ResearchTask"] = relationship("ResearchTask", back_populates="eval_results")

    __table_args__ = (
        CheckConstraint(
            "score IS NULL OR (score >= 0.0 AND score <= 1.0)",
            name="chk_score_range",
        ),
        Index("idx_eval_results_task", "task_id"),
        Index("idx_eval_results_type", "eval_type"),
        Index("idx_eval_results_task_type", "task_id", "eval_type"),
    )
