/**
 * API request and response types.
 * Generated from Pydantic models - do not edit manually.
 */

import type { ResearchResult, ResearchTask, TaskStatus } from "./research.js";

/** Request to create a new research task */
export interface CreateResearchRequest {
  /** Research query to investigate */
  query: string;
  /** URL to receive webhook notifications */
  webhook_url?: string | null;
  /** Maximum research iterations */
  max_iterations?: number;
}

/** Response after creating a research task */
export interface CreateResearchResponse {
  /** Unique task identifier */
  task_id: string;
  /** Initial task status */
  status: TaskStatus;
  /** Task creation timestamp (ISO 8601) */
  created_at: string;
}

/** Response when retrieving a research task */
export interface GetResearchResponse {
  /** The research task */
  task: ResearchTask;
}

/** Event types for SSE stream */
export type StreamEventType =
  | "task_created"
  | "task_started"
  | "step_completed"
  | "task_completed"
  | "task_failed"
  | "heartbeat";

/** A chunk in the research SSE stream */
export interface ResearchStreamChunk {
  /** Event type */
  event: StreamEventType;
  /** Event payload */
  data: Record<string, unknown>;
}

/** Standard error response */
export interface ErrorResponse {
  /** Error type or code */
  error: string;
  /** Human-readable error message */
  message: string;
  /** Additional error details */
  details?: Record<string, unknown> | null;
}

/** Service health status */
export type HealthStatus = "healthy" | "degraded" | "unhealthy";

/** Health check response */
export interface HealthResponse {
  /** Service health status */
  status: HealthStatus;
  /** API version */
  version: string;
  /** Response timestamp (ISO 8601) */
  timestamp: string;
}
