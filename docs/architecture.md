# Architecture

## Components

```text
frontend (Vite dev server :5173)          backend (uvicorn :8000)
┌──────────────────────────────┐          ┌───────────────────────────────────────┐
│ pages: Upload, Agent Map,    │  /health │ api/health.py                         │
│        Results               │ ───────► │                                       │
│ api/client.ts                │  /runs/* │ api/runs.py ── events/source.py       │
│ api/events.ts, api/graph.ts  │ ───────► │    │           (RunEventSource)       │
└──────────────────────────────┘  (proxy) │    └── agents/topology.py             │
                                          │ agents/ (LangGraph, to come)          │
                                          │   uses parsers/ chunkers/ embedders/  │
                                          │        retrievers/ evaluation/        │
                                          └───────────────────────────────────────┘
```

In dev, Vite proxies `/health` and `/runs/{id}/events|graph` to the backend, so the browser stays
same-origin. The SPA routes `/runs/{id}/map` and `/results` share the prefix and are not proxied.
Ports and hosts come from the root `.env`.

## Endpoints

| Method | Path | Returns |
| --- | --- | --- |
| GET | `/health` | `HealthResponse` (`status`, `version`) |
| GET | `/runs/{run_id}/events` | SSE stream of `AgentEvent` ([AGENTS.md](../AGENTS.md#sse-transport)) |
| GET | `/runs/{run_id}/graph` | `RunGraph` (static topology for now) |

## Event stream

The endpoint reads from a `RunEventSource` (a FastAPI dependency). The default
`EmptyEventSource` yields nothing, so the stream closes immediately. Phase 2 replaces it with
an event bus the agents publish to, which must replay events after a given `seq`. See
[ADR-002](../DECISIONS.md#adr-002-sse-with-seq-ids-for-the-event-stream).

## Pipeline components

`parsers`, `chunkers`, `embedders` and `retrievers` each expose an async ABC and a registry
([ADR-003](../DECISIONS.md#adr-003-async-component-interfaces-behind-name-registries)). Data
flows PDF → `ParsedDocument` (elements with page, type, bbox) → `Chunk`s (with provenance) →
vectors → `ScoredChunk`s.

## Wire types

Backend `WireModel`s serialize to camelCase JSON. `make schema` exports their JSON Schema to
`frontend/src/api/schema.json`; tests on both sides keep the TS mirror honest
([ADR-001](../DECISIONS.md#adr-001-backend-pydantic-models-own-the-wire-format)).
