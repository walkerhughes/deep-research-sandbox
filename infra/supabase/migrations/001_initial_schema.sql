-- Migration: 001_initial_schema
-- Description: Initial database schema for Deep Research Agent
-- Created: 2026-01-15

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Research tasks table
-- Stores the main research queries and their execution state
CREATE TABLE research_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    config JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, running, completed, failed
    result JSONB,
    reasoning_trace JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

-- Add constraint for valid status values
ALTER TABLE research_tasks
ADD CONSTRAINT chk_task_status
CHECK (status IN ('pending', 'running', 'completed', 'failed'));

-- Research findings table (normalized)
-- Stores individual findings from sub-queries during research
CREATE TABLE research_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE,
    sub_query TEXT NOT NULL,
    response TEXT NOT NULL,
    citations JSONB DEFAULT '[]',
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add constraint for confidence range
ALTER TABLE research_findings
ADD CONSTRAINT chk_confidence_range
CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0));

-- Inferences table (for eval tracking)
-- Tracks reasoning steps and inferences made during research
CREATE TABLE inferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE,
    claim TEXT NOT NULL,
    supporting_citations JSONB DEFAULT '[]',
    degrees_of_separation INT NOT NULL,
    reasoning TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add constraint for non-negative degrees of separation
ALTER TABLE inferences
ADD CONSTRAINT chk_degrees_non_negative
CHECK (degrees_of_separation >= 0);

-- Eval results table
-- Stores evaluation scores for research quality
CREATE TABLE eval_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE,
    eval_type TEXT NOT NULL,  -- reasoning_quality, hallucination, citation_accuracy, etc.
    score FLOAT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add constraint for score range
ALTER TABLE eval_results
ADD CONSTRAINT chk_score_range
CHECK (score IS NULL OR (score >= 0.0 AND score <= 1.0));

-- Add comments for documentation
COMMENT ON TABLE research_tasks IS 'Main table for research queries and their execution state';
COMMENT ON TABLE research_findings IS 'Normalized findings from research sub-queries';
COMMENT ON TABLE inferences IS 'Reasoning steps and inferences for eval tracking';
COMMENT ON TABLE eval_results IS 'Evaluation scores for research quality metrics';

COMMENT ON COLUMN research_tasks.status IS 'Task status: pending, running, completed, failed';
COMMENT ON COLUMN research_tasks.reasoning_trace IS 'Full reasoning trace for transparency';
COMMENT ON COLUMN research_findings.confidence IS 'Confidence score between 0.0 and 1.0';
COMMENT ON COLUMN inferences.degrees_of_separation IS 'Number of inference steps from source data';
