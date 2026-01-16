-- Migration: 002_add_indexes
-- Description: Add indexes for query performance
-- Created: 2026-01-15

-- Indexes for research_tasks
-- Index for filtering by status (common query pattern)
CREATE INDEX idx_tasks_status ON research_tasks(status);

-- Index for ordering by creation time (listing queries)
CREATE INDEX idx_tasks_created ON research_tasks(created_at DESC);

-- Composite index for status + created_at (common combined filter)
CREATE INDEX idx_tasks_status_created ON research_tasks(status, created_at DESC);

-- Indexes for research_findings
-- Index for looking up findings by task
CREATE INDEX idx_findings_task ON research_findings(task_id);

-- Index for ordering findings by creation time within a task
CREATE INDEX idx_findings_task_created ON research_findings(task_id, created_at);

-- Indexes for inferences
-- Index for looking up inferences by task
CREATE INDEX idx_inferences_task ON inferences(task_id);

-- Index for filtering by degrees of separation (eval queries)
CREATE INDEX idx_inferences_degrees ON inferences(degrees_of_separation);

-- Indexes for eval_results
-- Index for looking up eval results by task
CREATE INDEX idx_eval_results_task ON eval_results(task_id);

-- Index for filtering by eval type
CREATE INDEX idx_eval_results_type ON eval_results(eval_type);

-- Composite index for task + eval type (common query pattern)
CREATE INDEX idx_eval_results_task_type ON eval_results(task_id, eval_type);

-- GIN indexes for JSONB columns (for JSON querying)
-- Index for searching within task config
CREATE INDEX idx_tasks_config ON research_tasks USING GIN (config);

-- Index for searching within task metadata
CREATE INDEX idx_tasks_metadata ON research_tasks USING GIN (metadata);

-- Index for searching within citations
CREATE INDEX idx_findings_citations ON research_findings USING GIN (citations);

-- Index for searching within supporting citations
CREATE INDEX idx_inferences_citations ON inferences USING GIN (supporting_citations);

-- Add comments for documentation
COMMENT ON INDEX idx_tasks_status IS 'Filter tasks by status';
COMMENT ON INDEX idx_tasks_created IS 'Order tasks by creation time';
COMMENT ON INDEX idx_findings_task IS 'Look up findings for a task';
COMMENT ON INDEX idx_inferences_task IS 'Look up inferences for a task';
COMMENT ON INDEX idx_eval_results_task IS 'Look up eval results for a task';
