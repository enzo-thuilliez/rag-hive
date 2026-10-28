# CLAUDE.md

Instructions for Claude Code (and other agents) working in this repository.

## What this repo is

RAG Hive benchmarks RAG pipelines (parsing × chunking × embedding × retrieval) on a PDF with a
multi-agent LangGraph workflow, and streams the agents' work to a React dashboard. It is
local-first: Ollama for the LLM, BGE-M3 via sentence-transformers for embeddings, no paid API
at runtime (ADR-005). Claude Code is a dev tool here, not a runtime dependency. See
[README.md](README.md) for the pitch. See [AGENTS.md](AGENTS.md) for the agent workflow, the
event contract and the coding-agent workflow. Treat AGENTS.md as the spec.

**Current stage: scaffolding done, corpus next, see [ROADMAP.md](ROADMAP.md).** Interfaces,
registries, the event schema and the endpoints exist; no parser, chunker, embedder, retriever,
agent or evaluation logic does. Check before referencing a function or class as if it's real.

## Repository layout

A monorepo with two independent projects:

- `backend/`: Python 3.12 project managed with `uv` (its own `pyproject.toml` and `uv.lock`).
  src layout, package `rag_hive`:
  - `main.py`: `create_app()` factory. `config.py`: `Settings` (pydantic-settings).
  - `api/`: one router under `/api` (`/api/health`, `/api/runs/{run_id}/events` SSE,
    `/api/runs/{run_id}/graph`, docs at `/api/docs`). Every backend route goes under `/api`
    (ADR-004); a test fails otherwise.
  - `core/`: `WireModel` (camelCase JSON base), data models (`ParsedDocument`, `Chunk`,
    `ScoredChunk`), `Component` base and the generic `Registry`.
  - `parsers/`, `chunkers/`, `embedders/`, `retrievers/`: one async ABC + one registry each in
    `base.py`. Implementations go in sibling modules and register with `@<kind>_registry.register`.
  - `events/`: the `AgentEvent` schema, SSE framing, the injectable `RunEventSource`.
  - `agents/`: the LangGraph workflow (to come) and its static `topology.py`.
  - `evaluation/`: metrics for the Judge (to come).
  - `schema.py`: exports wire types to `frontend/src/api/schema.json` (`make schema`).
- `frontend/`: Vite + React + TypeScript app managed with pnpm. `src/api/` holds the typed
  client and the hand-written mirrors of backend wire types; `src/pages/` the routes.
- `docs/`: architecture notes. `data/`: local PDFs and outputs, gitignored.

## Conventions

- **Python**: `uv` only (`uv sync`, `uv run …`, `uv add …`), never `pip`. ruff with
  `select = ["ALL"]` and documented ignores; `mypy --strict` with the pydantic plugin. No `Any`
  without a comment saying why. Google-style docstrings on every public module, class and
  function (ruff `D` enforces it). Raise specific exceptions with a message built in a `msg`
  variable (ruff `EM`).
- **Config**: every tunable value is a `Settings` field, read from env / the root `.env`, and
  documented in `.env.example`. Never read `os.environ` directly or hardcode a URL, port, model
  or key.
- **Wire types**: backend Pydantic models extending `WireModel` are the source of truth. If you
  change one, run `make schema` and update the mirror in `frontend/src/api/` in the same commit;
  tests on both sides fail otherwise.
- **TypeScript**: `strict`, no `any`, typescript-eslint `strictTypeChecked`. TSDoc on every
  export (eslint-plugin-jsdoc enforces it). Prettier: double quotes, width 100.
- **Components** are async (`parse`, `chunk`, `embed_*`, `index`, `search`) and keep chunk
  provenance (page, element type, parent, bbox, parser).
- English only: code, comments, docs, commits.

## Running things locally

```bash
make install      # uv sync + pnpm install + pre-commit hooks
make dev          # backend :8000 (reload) + frontend :5173 (proxies /api)
make lint         # ruff check + format check, eslint, prettier check
make typecheck    # mypy --strict, tsc -b
make test         # pytest, vitest
make schema       # regenerate frontend/src/api/schema.json
make help
```

## Planned agent workflow

```text
Profiler → Planner → QA Generator → Workers (parallel, one per config) → Judge → Reporter
```

Not implemented yet. Each agent will emit `AgentEvent`s (`agent_started`, `tool_call`,
`progress`, `result`, `handoff`, `error`) through a `RunEventSource`. Details and invariants are
in [AGENTS.md](AGENTS.md#agent-workflow).

## Documentation

- **AGENTS.md**: agent and event contract, coding-agent workflow. If implementation must
  diverge from the contract, update AGENTS.md in the same change.
- **DECISIONS.md**: ADRs for decisions with trade-offs.
- **docs/architecture.md**: components, data flow, the SSE protocol.

## Claude Code notes

- `.claude/settings.json` allows the uv/pnpm/make commands, local git, `git push -u origin` for
  `feat/`, `fix/`, `chore/` and `docs/` branches, and `gh pr create`. Pushes to `main`, force
  pushes and `rm -rf` are denied.
- Project allow rules only load once the workspace is trusted: run `claude` interactively in
  the repo and accept the trust dialog. Until then only the deny rules apply.
- Follow the issue → branch → PR workflow in
  [AGENTS.md](AGENTS.md#workflow-for-coding-agents).
