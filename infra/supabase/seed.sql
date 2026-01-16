-- Seed Data for Development
-- This file contains sample data for local development and testing

-- Clear existing seed data (for re-running)
DELETE FROM eval_results WHERE task_id IN (
    SELECT id FROM research_tasks WHERE metadata->>'seed' = 'true'
);
DELETE FROM inferences WHERE task_id IN (
    SELECT id FROM research_tasks WHERE metadata->>'seed' = 'true'
);
DELETE FROM research_findings WHERE task_id IN (
    SELECT id FROM research_tasks WHERE metadata->>'seed' = 'true'
);
DELETE FROM research_tasks WHERE metadata->>'seed' = 'true';

-- Sample completed research task
INSERT INTO research_tasks (id, query, config, status, result, reasoning_trace, created_at, started_at, completed_at, metadata)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'What are the latest advances in transformer architectures for language models?',
    '{"max_iterations": 3, "depth": "deep", "sources": ["perplexity"]}',
    'completed',
    '{"summary": "Recent advances include mixture-of-experts, sparse attention, and state-space models...", "key_findings": ["MoE models achieve better scaling", "Flash attention reduces memory", "Mamba shows promise for long context"]}',
    '{"steps": [{"step": 1, "agent": "planner", "output": "Breaking down into sub-queries..."}], "total_tokens": 5000}',
    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '2 hours' + INTERVAL '5 seconds',
    NOW() - INTERVAL '1 hour',
    '{"seed": "true"}'
);

-- Sample pending research task
INSERT INTO research_tasks (id, query, config, status, created_at, metadata)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    'Compare React Server Components vs traditional SSR approaches',
    '{"max_iterations": 5, "depth": "shallow"}',
    'pending',
    NOW() - INTERVAL '30 minutes',
    '{"seed": "true"}'
);

-- Sample running research task
INSERT INTO research_tasks (id, query, config, status, created_at, started_at, metadata)
VALUES (
    '00000000-0000-0000-0000-000000000003',
    'What are best practices for implementing RAG systems in production?',
    '{"max_iterations": 4, "depth": "deep", "sources": ["perplexity", "web"]}',
    'running',
    NOW() - INTERVAL '10 minutes',
    NOW() - INTERVAL '9 minutes',
    '{"seed": "true"}'
);

-- Sample failed research task
INSERT INTO research_tasks (id, query, config, status, error, created_at, started_at, completed_at, metadata)
VALUES (
    '00000000-0000-0000-0000-000000000004',
    'Analyze proprietary internal database schema',
    '{}',
    'failed',
    'Access denied: Cannot access internal resources',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day' + INTERVAL '2 seconds',
    NOW() - INTERVAL '1 day' + INTERVAL '10 seconds',
    '{"seed": "true"}'
);

-- Sample research findings for completed task
INSERT INTO research_findings (task_id, sub_query, response, citations, confidence)
VALUES
(
    '00000000-0000-0000-0000-000000000001',
    'What is mixture-of-experts architecture?',
    'Mixture-of-experts (MoE) is an architecture where different "expert" neural networks specialize in different parts of the input space...',
    '[{"url": "https://arxiv.org/abs/2401.04088", "title": "Mixtral of Experts", "snippet": "We introduce Mixtral 8x7B..."}]',
    0.92
),
(
    '00000000-0000-0000-0000-000000000001',
    'How does Flash Attention improve transformer efficiency?',
    'Flash Attention is an IO-aware exact attention algorithm that reduces memory usage from O(N^2) to O(N)...',
    '[{"url": "https://arxiv.org/abs/2205.14135", "title": "FlashAttention", "snippet": "We propose FlashAttention..."}]',
    0.95
);

-- Sample inferences for completed task
INSERT INTO inferences (task_id, claim, supporting_citations, degrees_of_separation, reasoning)
VALUES
(
    '00000000-0000-0000-0000-000000000001',
    'MoE architectures are more parameter-efficient than dense models',
    '[{"url": "https://arxiv.org/abs/2401.04088"}]',
    1,
    'Direct claim from the Mixtral paper abstract stating 8x7B parameters with only 12.9B active'
),
(
    '00000000-0000-0000-0000-000000000001',
    'Combining MoE with Flash Attention could yield significant efficiency gains',
    '[{"url": "https://arxiv.org/abs/2401.04088"}, {"url": "https://arxiv.org/abs/2205.14135"}]',
    2,
    'Inference: MoE reduces active parameters, Flash Attention reduces memory. Combining both could multiply benefits.'
);

-- Sample eval results for completed task
INSERT INTO eval_results (task_id, eval_type, score, details)
VALUES
(
    '00000000-0000-0000-0000-000000000001',
    'reasoning_quality',
    0.85,
    '{"strengths": ["Clear logical chain", "Good source usage"], "weaknesses": ["Could explore more alternatives"]}'
),
(
    '00000000-0000-0000-0000-000000000001',
    'citation_accuracy',
    0.95,
    '{"verified_citations": 2, "total_citations": 2, "issues": []}'
);

-- Verify seed data
SELECT
    'research_tasks' as table_name,
    COUNT(*) as count
FROM research_tasks WHERE metadata->>'seed' = 'true'
UNION ALL
SELECT 'research_findings', COUNT(*) FROM research_findings WHERE task_id IN (
    SELECT id FROM research_tasks WHERE metadata->>'seed' = 'true'
)
UNION ALL
SELECT 'inferences', COUNT(*) FROM inferences WHERE task_id IN (
    SELECT id FROM research_tasks WHERE metadata->>'seed' = 'true'
)
UNION ALL
SELECT 'eval_results', COUNT(*) FROM eval_results WHERE task_id IN (
    SELECT id FROM research_tasks WHERE metadata->>'seed' = 'true'
);
