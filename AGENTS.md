# AGENTS.md

This file has two parts: the contract for RAG Hive's own agents and events, then the
workflow for coding agents (Claude Code, Codex, Cursor...) working on this repo. Humans: the
same workflow is in [CONTRIBUTING.md](CONTRIBUTING.md).

> Status: contract and typed stubs. The event schema, the workflow graph, the component
> interfaces and every agent's input/output models exist in code; no agent logic does.

**Language:** everything in this repository is written in English (docs, code, comments,
docstrings, commit messages, event text, error messages), even when the person asking for the
change writes in another language.

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

- **Never commit or push to `main`.** One issue → one branch (`<type>/<short-slug>`, `<type>`
  one of `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`) → one PR with
  `Closes #N` → CI green → squash merge by the product owner. Once CI is green, stop: never
  merge, enable auto-merge or approve your own PR.
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
- **CHANGELOG**: one bullet under `Unreleased` in [CHANGELOG.md](CHANGELOG.md), added in its
  own last commit. Never edit existing bullets.
- **Conflicts**: merge `main` into the branch. Never rebase, never force push (denied by
  `.claude/settings.json`).
- **Dependencies**: ask before adding one. Python with `uv add`, frontend with `pnpm add`.
- **GitHub**: use `gh api` (REST) for issues and PRs.
- **Frontend changes**: before/after screenshots in the PR.
- **Before pushing**: `make lint`, `make typecheck`, `make test`. CI runs the same.
- **Decisions and contracts**: a decision with trade-offs gets an ADR in
  [DECISIONS.md](DECISIONS.md). A contract change updates this file in the same PR.
