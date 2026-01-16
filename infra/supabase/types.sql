-- Custom Types for Deep Research Agent
-- This file contains custom PostgreSQL types used across the schema

-- Task status enum type (alternative to CHECK constraint)
-- Note: Using TEXT with CHECK constraint in migrations for flexibility,
-- but this type can be used if strict typing is preferred
DO $$ BEGIN
    CREATE TYPE task_status AS ENUM ('pending', 'running', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Eval type enum for evaluation categories
DO $$ BEGIN
    CREATE TYPE eval_type AS ENUM (
        'reasoning_quality',      -- Quality of reasoning chain
        'hallucination',          -- Hallucination detection
        'citation_accuracy',      -- Citation verification
        'inference_validity',     -- Validity of inferences
        'source_relevance',       -- Relevance of sources used
        'completeness'            -- Completeness of research
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Citation structure type (for documentation, actual storage uses JSONB)
-- Structure: {
--   "url": "https://...",
--   "title": "...",
--   "snippet": "...",
--   "accessed_at": "2026-01-15T..."
-- }

-- Config structure type (for documentation)
-- Structure: {
--   "max_iterations": 5,
--   "depth": "deep" | "shallow",
--   "sources": ["perplexity", "web"],
--   "timeout_seconds": 300
-- }

-- Reasoning trace structure type (for documentation)
-- Structure: {
--   "steps": [
--     {
--       "step": 1,
--       "agent": "planner",
--       "input": "...",
--       "output": "...",
--       "reasoning": "...",
--       "timestamp": "..."
--     }
--   ],
--   "total_tokens": 12345,
--   "model_calls": 8
-- }
