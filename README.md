# RAG Hive

**Find the best RAG pipeline for your PDF. A hive of agents benchmarks them while you watch.**

[![CI](https://github.com/enzo-thuilliez/rag-hive/actions/workflows/ci.yml/badge.svg)](https://github.com/enzo-thuilliez/rag-hive/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Whether a RAG system answers well depends on four choices: how the PDF is parsed, how it is
chunked, how chunks are embedded and how they are retrieved. The best combination changes from
one document to the next, and trying them by hand is slow. RAG Hive takes a PDF, generates
questions about it, runs every candidate pipeline in parallel, scores them and shows the
results in a dashboard. A live map lets you watch the agents do the work.

> **Status:** scaffolding. The backend, frontend, CI and interfaces are in place. No parser,
> chunker, embedder, retriever or agent is implemented yet. See [ROADMAP.md](ROADMAP.md).

## What it does

- **Profile the document.** Detect what the PDF holds (tables, images, layout, length) to pick
  sensible candidates.
- **Plan the grid.** Choose parsing × chunking × embedding × retrieval configs to compare.
- **Generate questions.** Build a QA set grounded in the document, with source pages.
- **Benchmark in parallel.** One worker per pipeline config indexes the PDF and answers the QA set.
- **Judge and report.** Score retrieval and answers, then rank the pipelines.
- **Watch it live.** Agents stream typed events to an agent map and a results dashboard.

## How it works

```text
  PDF ──► FastAPI ──► LangGraph workflow
                      Profiler → Planner → QA Generator ─┬─► Worker ─┐
                                                         ├─► Worker ─┼─► Judge → Reporter
                                                         └─► Worker ─┘
                            │
                            │ typed agent events (SSE)
                            ▼
                      React dashboard: agent map + results
```

1. Pipeline components (parsers, chunkers, embedders, retrievers) implement small async
   interfaces and register by name, so the Planner can build any combination from a config.
2. Each agent emits typed events (`agent_started`, `tool_call`, `progress`, `result`, `handoff`,
   `error`), streamed over SSE with resume support.
3. The frontend draws the workflow graph from `/api/runs/{id}/graph` and animates it from the
   event stream. The backend serves only `/api`; every other path belongs to the frontend.

More in [docs/architecture.md](docs/architecture.md) and [AGENTS.md](AGENTS.md).

## Stack

| Layer | Tech |
| --- | --- |
| API | Python 3.12, [FastAPI](https://fastapi.tiangolo.com/), pydantic-settings, [`uv`](https://docs.astral.sh/uv/) |
| Agents | [LangGraph](https://github.com/langchain-ai/langgraph), Anthropic + OpenAI (provider-agnostic) |
| Dashboard | React, TypeScript, Vite, Tailwind, [React Flow](https://reactflow.dev/), [Recharts](https://recharts.org/) |
| Quality | ruff, mypy `--strict`, pytest, typescript-eslint (type-aware), Prettier, Vitest, pre-commit |

## Development

Requires Python 3.12 with `uv`, Node 24 with pnpm (via corepack), and `make`.

```sh
cp .env.example .env   # add your API keys
make install           # uv sync, pnpm install, git hooks
make dev               # backend on :8000 + frontend on :5173
make lint              # ruff, eslint, prettier
make typecheck         # mypy --strict, tsc
make test              # pytest, vitest
```

`make help` lists every target.

## Repository layout

```text
backend/     FastAPI app, LangGraph agents, pipeline components (Python, uv)
frontend/    React dashboard (Vite, pnpm)
docs/        architecture notes
data/        local PDFs and results (gitignored)
```

## License

[MIT](LICENSE)
