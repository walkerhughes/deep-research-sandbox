/**
 * Deep Research Shared Types
 *
 * This package provides TypeScript type definitions for the Deep Research Agent API.
 * Types are generated from Pydantic models to ensure consistency between
 * the Python backend and TypeScript frontend.
 *
 * @packageDocumentation
 */

// Research types
export type {
  TaskStatus,
  Citation,
  Inference,
  ReasoningStep,
  ResearchResult,
  ResearchTask,
} from "./research.js";

// Event types
export type {
  EventType,
  BaseEvent,
  TaskCreatedEvent,
  TaskStartedEvent,
  StepCompletedEvent,
  TaskCompletedEvent,
  TaskFailedEvent,
  StreamEvent,
} from "./events.js";

// API types
export type {
  CreateResearchRequest,
  CreateResearchResponse,
  GetResearchResponse,
  StreamEventType,
  ResearchStreamChunk,
  ErrorResponse,
  HealthStatus,
  HealthResponse,
} from "./api.js";
