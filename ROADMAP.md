# Roadmap

Phased plan for this project. Each phase has one objective, concrete deliverables, and a status.
For *what* each part should do once built, see [AGENTS.md](AGENTS.md).

**Status legend:** ✅ Done · 🚧 In progress · ⬜ To do

## Phase 0: Scaffolding

**Objective:** a green skeleton so feature work can start without friction.

- [x] Monorepo: `backend/` (uv, FastAPI) and `frontend/` (Vite, React, TS, Tailwind)
- [x] `/api/health`, SSE `/api/runs/{id}/events` with `Last-Event-ID` resume,
      `/api/runs/{id}/graph`
- [x] Async component interfaces and registries; chunk provenance model
- [x] Agent event schema, mirrored in TS with a schema sync check
- [x] Makefile, pre-commit (ruff, mypy, eslint, prettier, tsc, conventional commits), CI
- [x] README, CLAUDE.md, AGENTS.md, CONTRIBUTING, DECISIONS, MIT license

**Status: ✅ Done**

## Phase 1: Pipeline components

**Objective:** enough real components to make a benchmark meaningful.

- [ ] Parsers: a fast text parser and a layout-aware parser
- [ ] Chunkers: fixed-size, recursive, and one structure-aware (hierarchical) strategy
- [ ] Embedders: OpenAI, plus one local model
- [ ] Retrievers: dense, BM25, hybrid
- [ ] Run one pipeline end to end on a sample PDF from a script

**Status: ⬜ To do**

## Phase 2: Agent workflow

**Objective:** the LangGraph workflow, streaming real events.

- [ ] Provider-agnostic LLM client (Anthropic, OpenAI) from `Settings`
- [ ] Event bus implementing `RunEventSource` with replay
- [ ] Profiler, Planner, QA Generator, Workers (parallel), Judge, Reporter
- [ ] Run creation endpoint (upload a PDF, start a run)

**Status: ⬜ To do**

## Phase 3: Dashboard

**Objective:** watch a run live and read its results.

- [ ] Upload page wired to run creation
- [ ] Agent map: React Flow graph from `/graph`, animated from the event stream
- [ ] Results: Recharts comparison of pipelines, drill-down to retrieved chunks

**Status: ⬜ To do**

## Phase 4: Evaluation quality

**Objective:** trustworthy scores.

- [ ] Retrieval metrics (recall@k, MRR, nDCG) and answer metrics (faithfulness, correctness)
- [ ] Judge calibration on a hand-labelled sample
- [ ] Cost and latency per pipeline

**Status: ⬜ To do**
