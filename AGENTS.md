# AGENTS.md

The single source of instructions for coding agents (Claude Code, Codex, Cursor...) on this
repo; `CLAUDE.md` only imports it. Three parts: how to work in the repo, the contract for RAG
Hive's own agents and events, then the issue → branch → PR workflow. Humans: the same workflow
is in [CONTRIBUTING.md](CONTRIBUTING.md).

> **Current stage: scaffolding and corpus done, golden set next** ([ROADMAP.md](ROADMAP.md)).
> Every planned module exists as a typed stub: models, interfaces and docstrings, with bodies
> that raise `NotImplementedError` (module map in
> [docs/architecture.md](docs/architecture.md#module-map)). The registries, the event schema,
> the endpoints and the workflow wiring are real; no parser, chunker, embedder, retriever, LLM,
> agent or metric logic is. Check before calling a function as if it works. Stub signatures
> are frozen: changing one needs an ADR (ADR-006).

**Language:** everything in this repository is written in English (docs, code, comments,
docstrings, commit messages, event text, error messages), even when the person asking for the
change writes in another language.

## Working in this repo

RAG Hive is local-first: Ollama for the LLM, BGE-M3 via sentence-transformers for
embeddings, no paid API at runtime (ADR-005). Coding agents are dev tools here, not runtime
dependencies.

### Repository layout

A monorepo with two independent projects:

- `backend/`: Python 3.12 project managed with `uv` (its own `pyproject.toml` and `uv.lock`).
  src layout, package `rag_hive`:
  - `main.py`: `create_app()` factory. `config.py`: `Settings` (pydantic-settings).
  - `api/`: one router under `/api` (`/api/health`, `/api/runs/{run_id}/events` SSE,
    `/api/runs/{run_id}/graph`, docs at `/api/docs`). Every backend route goes under `/api`
    (ADR-004); a test fails otherwise.
  - `core/`: `WireModel` (camelCase JSON base), `DataModel` (snake_case base for repo files
    and agent state), data models (`ParsedDocument`, `Chunk`, `ScoredChunk`), `Component` base
    and the generic `Registry`.
  - `parsers/`, `chunkers/`, `embedders/`, `retrievers/`: one async ABC + one registry each in
    `base.py`. Implementations go in sibling modules and register with `@<kind>_registry.register`.
    `embedders/sentence_transformer.py` is the default (BGE-M3).
  - `llm/`: `LLMProvider` ABC, `llm_registry`, `create_llm`; `ollama.py` is the only provider.
  - `events/`: the `AgentEvent` schema, SSE framing, the injectable `RunEventSource`.
  - `agents/`: one module per agent (input/output models, `run_*`, LangGraph node),
    `state.py` (`WorkflowState`), `graph.py` (the topology, the `StateGraph` and the `RunGraph`
    served to the dashboard), `topology.py` (`RunGraph` wire types).
  - `corpus/`: `CorpusEntry` / `CorpusManifest`, manifest loading, the checksum-verified
    downloader, image-only derived files (`derive.py`) and `python -m rag_hive.corpus`
    (`make corpus`).
  - `evaluation/`: `golden.py` (`GoldenQuestion`), `span_matching.py`, `metrics/retrieval.py`,
    `metrics/parsing.py`.
  - `schema.py`: `make schema` exports wire types to `frontend/src/api/schema.json` and the
    `CorpusEntry` / `GoldenQuestion` schemas to `docs/schemas/`.
- `frontend/`: Vite + React + TypeScript app managed with pnpm. `src/api/` holds the typed
  client and the hand-written mirrors of backend wire types; `src/pages/` the routes.
- `docs/`: architecture notes and generated data schemas. `data/`: local PDFs and outputs,
  gitignored, except `data/corpus/manifest.yaml`. Never commit a PDF.

### Conventions

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

### Commands

```bash
make install      # uv sync + pnpm install + pre-commit hooks
make dev          # backend :8000 (reload) + frontend :5173 (proxies /api)
make lint         # ruff check + format check, eslint, prettier check
make typecheck    # mypy --strict, tsc -b
make test         # pytest, vitest
make schema       # regenerate frontend/src/api/schema.json and docs/schemas/
make corpus       # download + verify the corpus PDFs into data/corpus/raw/ (never committed)
make help
```

### Docs to keep in sync

- **AGENTS.md**: agent and event contract, coding-agent workflow. If implementation must
  diverge from the contract, update AGENTS.md in the same change.
- **DECISIONS.md**: ADRs for decisions with trade-offs.
- **docs/architecture.md**: components, data flow, the SSE protocol.
- **ROADMAP.md**: move an item to Done when a PR completes it; each step matches a milestone.

### Code intelligence

This repo is indexed with **GitNexus** (mostly code; the corpus PDFs are never committed).

- Refresh: `gitnexus analyze` at the repo root (the hooks also reindex after commits).
- Before changing a registry, a wire type, an agent's input/output model or any function used
  across modules, run GitNexus impact analysis and list the affected callers in the PR.
- Start exploring from the clusters and processes resources; `docs/architecture.md` has the
  module map.

## Agent workflow

```text
Profiler → Planner → QA Generator → Workers (parallel) → Judge → Reporter
```

| Agent | Input | Output |
| --- | --- | --- |
| Profiler | The PDF | Document profile: pages, text density, tables, images, layout |
| Planner | Profile, registered components | Grid of pipeline configs (parser × chunker × embedder × retriever) |
| QA Generator | The PDF | Questions with reference answers and source pages |
| Worker (one per config) | One config, the PDF, the QA set | Retrieved chunks and answers per question |
| Judge | All worker outputs | Retrieval and answer scores per config |
| Reporter | Scores | Ranking and summary for the dashboard |

Each agent module in [`agents/`](backend/src/rag_hive/agents/) defines its input model (the
`WorkflowState` keys it reads), its output model, a `run_*` function and a LangGraph node that
returns only the keys it writes. Workers get their `WorkerInput` through LangGraph's `Send`, one
per config, and append to `worker_outputs`. Questions use the golden-set format
(`GoldenQuestion`) whether they come from the golden set or the LLM.

The topology is declared once in [`agents/graph.py`](backend/src/rag_hive/agents/graph.py):
`build_workflow` wires the LangGraph `StateGraph` from it and `GET /api/runs/{run_id}/graph`
serves it, so the agent map matches the graph that runs. The `worker` node is a template;
actual workers are created at runtime.

### Design principles

1. **Components come from registries.** The Planner only proposes names that are registered in
   `parser_registry`, `chunker_registry`, `embedder_registry` and `retriever_registry`, and
   builds them with `registry.create(name, config)`. No agent instantiates a component class
   directly.
2. **Scores come from evaluation code.** The Judge may use an LLM as a grader, but every number
   on the dashboard traces back to a metric in `rag_hive.evaluation`, never to free text.
3. **Provenance is kept end to end.** A `Chunk` keeps its page, element type, parent, bbox and
   parser, so any retrieved passage can be shown in the PDF.
4. **Local-first, provider-agnostic.** Agents and embedders go through the provider set in
   `Settings` (`LLM_PROVIDER`, `EMBEDDING_PROVIDER`), never through a hardcoded SDK client.
   Runtime providers are local: Ollama for the LLM, sentence-transformers (BGE-M3) for
   embeddings. No paid API is called at runtime
   ([ADR-005](DECISIONS.md#adr-005-local-first-no-paid-api-at-runtime)).
5. **Failures are events.** An agent that fails emits an `error` event with the actual reason;
   a failing worker does not stop the other workers.

## Event contract

Source of truth: [`events/schema.py`](backend/src/rag_hive/events/schema.py). TypeScript mirror:
[`frontend/src/api/events.ts`](frontend/src/api/events.ts). JSON is camelCase.

Every event carries `runId`, `seq`, `timestamp`, `agent`, `agentInstanceId`,
`parentInstanceId`, and a `type`:

| `type` | Payload | Emitted when |
| --- | --- | --- |
| `agent_started` | `task` | An agent begins |
| `tool_call` | `tool`, `arguments` | An agent calls a tool |
| `progress` | `message`, `fraction` (0–1 or null) | A long step advances |
| `result` | `summary`, `data` | An agent produces its output |
| `handoff` | `toAgent`, `toInstanceId`, `reason` | Control passes to another agent |
| `error` | `message`, `recoverable` | An agent fails |

Invariants:

- `seq` starts at 0 and strictly increases within a run. It is the SSE `id`.
- Singleton agents leave `agentInstanceId` null. Workers set it (`worker-<n>`) and set
  `parentInstanceId` to the agent that spawned them, so the map can attach them.
- An agent's events are bracketed by `agent_started` and either `result` or `error`.
- Adding a field or an event type is a contract change: update the schema, run `make schema`,
  update the TS mirror and this table in the same PR.

### SSE transport

`GET /api/runs/{run_id}/events` streams `text/event-stream` frames:

```text
id: <seq>
event: <type>
data: <event JSON>
```

A client that reconnects sends `Last-Event-ID: <seq>` and receives only later events. A
non-integer `Last-Event-ID` returns 400.

## Workflow for coding agents

- **Never commit or push to `main`.** One issue → one branch (`<type>/<issue>-<short-slug>`,
  e.g. `feat/14-pdfplumber-parser`; `<type>` one of `feat`, `fix`, `chore`, `docs`, `refactor`,
  `test`, `perf`, `ci`) → one PR with `Closes #N` → CI green → squash merge by the product
  owner. Once CI is green, stop: never merge, enable auto-merge or approve your own PR.
- **Issues**: every issue has one `type:*` label, one or more `area:*` labels, one
  `priority:p0|p1|p2` label and the milestone of its roadmap step. A PR with no issue gets one
  first.
- **Docs-only changes** go in their own small PR, never mixed into a code PR.
- **Start**: read the issue, every issue in its Dependencies, and the AGENTS.md / DECISIONS.md
  sections it cites. If a dependency is still open, stop and say so.
- **Scope**: anything not in the issue's Acceptance goes under "Left for later" in the PR
  body, not in the code.
- **PR body**: first line `Closes #N`, or `Part of #N` when the PR is one step. Then What, How,
  Tests, Left for later.
- **Commits**: conventional, `type(scope): lowercase summary`, checked by the commit-msg hook.
  Scopes: `backend`, `frontend`, `agents`, `events`, `eval`, `corpus`, `docs`, `ci`, `deps`,
  `repo`.
- **CHANGELOG**: written by release-please from squash-merge titles. Never edit
  [CHANGELOG.md](CHANGELOG.md) by hand; make the PR title a good changelog line instead.
- **Conflicts**: merge `main` into the branch. Never rebase, never force push (denied by
  `.claude/settings.json`).
- **Dependencies**: ask before adding one. Python with `uv add`, frontend with `pnpm add`.
- **GitHub**: use `gh api` (REST) for issues and PRs.
- **Frontend changes**: before/after screenshots in the PR.
- **Before pushing**: `make lint`, `make typecheck`, `make test`. CI runs the same.
- **Decisions and contracts**: a decision with trade-offs gets an ADR in
  [DECISIONS.md](DECISIONS.md). A contract change updates this file in the same PR.
