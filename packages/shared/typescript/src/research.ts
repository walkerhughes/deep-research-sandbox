/**
 * Research-related types.
 * Generated from Pydantic models - do not edit manually.
 */

/** Status of a research task */
export type TaskStatus = "pending" | "running" | "completed" | "failed";

/** A citation from a research source */
export interface Citation {
  /** Title of the source */
  title: string;
  /** URL of the source */
  url: string;
  /** Relevant excerpt from the source */
  snippet: string;
}

/** An inference derived from research findings */
export interface Inference {
  /** The inference or claim being made */
  claim: string;
  /** IDs or URLs of citations supporting this inference */
  supporting_citations: string[];
  /** How many logical steps from direct evidence */
  degrees_of_separation: number;
  /** Explanation of the reasoning chain */
  reasoning: string;
}

/** A step in the research agent's reasoning trace */
export interface ReasoningStep {
  /** Sequential step number */
  step_number: number;
  /** Action taken (e.g., 'search', 'analyze', 'synthesize') */
  action: string;
  /** Input to this step */
  input: string;
  /** Output from this step */
  output: string;
  /** Why this action was taken */
  rationale: string;
}

/** Complete result of a research task */
export interface ResearchResult {
  /** Executive summary of findings */
  summary: string;
  /** Bullet-point key findings */
  key_findings: string[];
  /** Inferences derived from research */
  inferences: Inference[];
  /** Step-by-step reasoning trace */
  reasoning_trace: ReasoningStep[];
  /** All citations used in research */
  citations: Citation[];
  /** Confidence in the results (0-1) */
  confidence_score: number;
}

/** A research task with its status and results */
export interface ResearchTask {
  /** Unique task identifier */
  id: string;
  /** Original research query */
  query: string;
  /** Current task status */
  status: TaskStatus;
  /** Research result if completed */
  result: ResearchResult | null;
  /** Error message if failed */
  error_message: string | null;
  /** Task creation time (ISO 8601) */
  created_at: string;
  /** When task started running (ISO 8601) */
  started_at: string | null;
  /** Task completion time (ISO 8601) */
  completed_at: string | null;
}
