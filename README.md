# Deep Research Agent

A multi-step iterative research agent that performs deep research with reasoning traces, citations, and real-time streaming updates.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Vercel)                             │
│  ├── Next.js App                                                        │
│  ├── Chat Interface                                                     │
│  ├── Orchestrator Agent (Vercel AI SDK)                                │
│  └── Webhook Receiver                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP / Webhooks
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (Modal)                               │
│  ├── FastAPI                                                            │
│  │   ├── POST /research                                                 │
│  │   ├── GET /research/{id}                                             │
│  │   └── GET /research/{id}/stream                                      │
│  └── Research Pipeline (Pydantic AI)                                    │
│      ├── PlannerAgent                                                   │
│      ├── ResearcherAgent → Perplexity Sonar MCP                        │
│      └── SynthesizerAgent                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER (Supabase)                           │
│  ├── research_tasks                                                     │
│  ├── research_findings                                                  │
│  └── inferences                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
deep-research-sandbox/
├── apps/
│   ├── api/              # FastAPI backend (Python)
│   └── web/              # Next.js frontend
├── packages/
│   └── shared/           # Shared types
│       ├── python/       # Python shared types
│       └── typescript/   # TypeScript shared types
├── evals/                # Evaluation suite
│   ├── generators/       # Test case generators
│   ├── judges/           # LLM judges for reasoning quality
│   ├── runners/          # Eval execution
│   ├── metrics/          # Metrics collection
│   └── datasets/         # Test datasets
├── infra/                # Infrastructure config
│   ├── supabase/         # Database migrations
│   └── modal/            # Modal deployment config
├── pyproject.toml        # Root workspace config
├── .pre-commit-config.yaml
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [pnpm](https://pnpm.io/) (Node.js package manager)

## Getting Started

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-org/deep-research-sandbox.git
cd deep-research-sandbox

# Install Python dependencies (from root)
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY, PERPLEXITY_API_KEY, SUPABASE_*, MODAL_*
```

### 3. Run Development Servers

```bash
# Backend API (FastAPI)
cd apps/api
uv run uvicorn src.main:app --reload

# Frontend (Next.js) - in another terminal
cd apps/web
pnpm install
pnpm dev
```

## Development

### Code Quality

```bash
# Run linting
uv run ruff check .

# Run formatting
uv run ruff format .
uv run black .

# Run type checking
uv run mypy .

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_agents.py
```

### Evaluations

```bash
# Run evaluation suite
cd evals
uv run python -m runners.run_evals
```

## Key Technologies

| Component     | Technology              | Purpose                       |
| ------------- | ----------------------- | ----------------------------- |
| Backend       | FastAPI + Pydantic AI   | Research agent orchestration  |
| Frontend      | Next.js + Vercel AI SDK | Chat interface & orchestrator |
| Database      | Supabase (PostgreSQL)   | Data persistence & realtime   |
| Compute       | Modal                   | Serverless GPU/CPU execution  |
| Search        | Perplexity Sonar MCP    | Web search capabilities       |
| Observability | LangSmith + OTEL        | Tracing & monitoring          |
| Evals         | Custom LLM Judges       | Reasoning quality assessment  |

## Environment Variables

See [`.env.example`](.env.example) for all required environment variables.

| Variable               | Required | Description                   |
| ---------------------- | -------- | ----------------------------- |
| `OPENAI_API_KEY`       | Yes      | OpenAI API key for LLM calls  |
| `PERPLEXITY_API_KEY`   | Yes      | Perplexity API for web search |
| `SUPABASE_URL`         | Yes      | Supabase project URL          |
| `SUPABASE_ANON_KEY`    | Yes      | Supabase anonymous key        |
| `SUPABASE_SERVICE_KEY` | Yes      | Supabase service role key     |
| `MODAL_TOKEN_ID`       | Yes      | Modal token ID                |
| `MODAL_TOKEN_SECRET`   | Yes      | Modal token secret            |
| `LANGSMITH_API_KEY`    | No       | LangSmith for tracing         |

## License

MIT
