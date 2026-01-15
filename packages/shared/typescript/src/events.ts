/**
 * Webhook and stream event types.
 * Generated from Pydantic models - do not edit manually.
 */

import type { ReasoningStep, ResearchResult } from "./research.js";

/** Types of events that can be emitted */
export type EventType =
  | "task_created"
  | "task_started"
  | "step_completed"
  | "task_completed"
  | "task_failed";

/** Base model for all events */
export interface BaseEvent {
  /** Type of event */
  event_type: EventType;
  /** ID of the associated task */
  task_id: string;
  /** Event timestamp (ISO 8601) */
  timestamp: string;
}

/** Event emitted when a task is created */
export interface TaskCreatedEvent extends BaseEvent {
  event_type: "task_created";
  /** Research query */
  query: string;
}

/** Event emitted when task execution begins */
export interface TaskStartedEvent extends BaseEvent {
  event_type: "task_started";
}

/** Event emitted when a reasoning step completes */
export interface StepCompletedEvent extends BaseEvent {
  event_type: "step_completed";
  /** The completed reasoning step */
  step: ReasoningStep;
}

/** Event emitted when a task completes successfully */
export interface TaskCompletedEvent extends BaseEvent {
  event_type: "task_completed";
  /** Final research result */
  result: ResearchResult;
}

/** Event emitted when a task fails */
export interface TaskFailedEvent extends BaseEvent {
  event_type: "task_failed";
  /** Error message */
  error: string;
  /** Additional error info */
  error_details: Record<string, unknown> | null;
}

/** Union type for all events */
export type StreamEvent =
  | TaskCreatedEvent
  | TaskStartedEvent
  | StepCompletedEvent
  | TaskCompletedEvent
  | TaskFailedEvent;
