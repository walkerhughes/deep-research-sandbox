# Shared Types Package

This package provides type definitions that are shared between the Python backend and TypeScript frontend to ensure API contract consistency.

## Structure

```
packages/shared/
├── python/
│   ├── pyproject.toml
│   └── shared_types/
│       ├── __init__.py
│       ├── research.py      # Research-related models
│       ├── events.py        # Webhook/stream events
│       ├── api.py           # API request/response models
│       └── py.typed         # PEP 561 marker
└── typescript/
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── index.ts
        ├── research.ts
        ├── events.ts
        └── api.ts
```

## Usage

### Python Backend

```python
from shared_types import ResearchTask, ResearchResult, TaskStatus

@app.post("/research")
async def create_research(request: CreateResearchRequest) -> CreateResearchResponse:
    task = ResearchTask(
        id=str(uuid4()),
        query=request.query,
        status=TaskStatus.PENDING,
    )
    # ... process task
    return CreateResearchResponse(
        task_id=task.id,
        status=task.status,
        created_at=task.created_at,
    )
```

### TypeScript Frontend

```typescript
import type { ResearchTask, CreateResearchRequest } from '@deep-research/shared';

async function createResearch(query: string): Promise<ResearchTask> {
  const request: CreateResearchRequest = { query };
  const response = await fetch('/api/research', {
    method: 'POST',
    body: JSON.stringify(request),
  });
  return response.json();
}
```

## Type Synchronization Workflow

### Manual Synchronization (Current)

The TypeScript types are manually written to match the Pydantic models. When modifying types:

1. Update the Pydantic model in `packages/shared/python/shared_types/`
2. Update the corresponding TypeScript type in `packages/shared/typescript/src/`
3. Run tests to verify both are consistent

### Automated Generation (Optional)

For automated TypeScript generation from Pydantic models:

```bash
# Install generation dependencies
cd packages/shared/python
pip install pydantic-to-typescript

# Generate TypeScript types
python scripts/generate_types.py

# Or use npm script
cd packages/shared/typescript
npm run generate
```

The generated types will be placed in `packages/shared/typescript/src/generated.ts`.

## Type Categories

### Research Types (`research.py` / `research.ts`)

Core domain models for research tasks:

- `TaskStatus` - Enum: pending, running, completed, failed
- `Citation` - Source reference with title, URL, snippet
- `Inference` - Derived conclusion with reasoning chain
- `ReasoningStep` - Single step in research process
- `ResearchResult` - Complete research output
- `ResearchTask` - Task with status and result

### Event Types (`events.py` / `events.ts`)

Webhook and streaming event models:

- `TaskCreatedEvent` - Task was created
- `TaskStartedEvent` - Task execution began
- `StepCompletedEvent` - Reasoning step finished
- `TaskCompletedEvent` - Task completed successfully
- `TaskFailedEvent` - Task failed with error

### API Types (`api.py` / `api.ts`)

Request and response models:

- `CreateResearchRequest` - Create new research task
- `CreateResearchResponse` - Response after creation
- `GetResearchResponse` - Task retrieval response
- `ResearchStreamChunk` - SSE stream chunk
- `ErrorResponse` - Standard error format
- `HealthResponse` - Health check response

## Validation Rules

Python Pydantic models include validation:

- `CreateResearchRequest.query`: 1-2000 characters
- `CreateResearchRequest.max_iterations`: 1-20
- `ResearchResult.confidence_score`: 0.0-1.0
- `Inference.degrees_of_separation`: >= 1

TypeScript types are structural only; validation should be performed on the backend.

## CI Validation

The CI pipeline validates type consistency:

```yaml
# .github/workflows/ci.yml
- name: Validate Types
  run: |
    # Run Python type tests
    pytest tests/unit/test_shared_types.py

    # Type check Python
    mypy packages/shared/python

    # Type check TypeScript
    cd packages/shared/typescript && npm run build
```
