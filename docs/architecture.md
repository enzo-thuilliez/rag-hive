# Architecture

## Components

```text
frontend (Vite dev server :5173)          backend (uvicorn :8000)
┌──────────────────────────────┐          ┌───────────────────────────────────────┐
│ pages: Upload, Agent Map,    │          │ api/ (router, prefix /api)            │
│        Results               │  /api/*  │   health.py                           │
│ api/client.ts                │ ───────► │   runs.py ── events/source.py         │
│ api/events.ts, api/graph.ts  │          │    │         (RunEventSource)         │
└──────────────────────────────┘  (proxy) │    └── agents/topology.py             │
                                          │ agents/ (LangGraph, to come)          │
                                          │   uses parsers/ chunkers/ embedders/  │
                                          │        retrievers/ evaluation/        │
                                          └───────────────────────────────────────┘
```

Every backend route, the OpenAPI docs included, lives under `/api`; every other path belongs to
the frontend ([ADR-004](../DECISIONS.md#adr-004-every-backend-route-lives-under-api)). In dev,
Vite proxies `/api` to the backend, so the browser stays same-origin. In production the same
split lets one origin serve both. Ports and hosts come from the root `.env`.

## Endpoints

| Method | Path | Returns |
| --- | --- | --- |
| GET | `/api/health` | `HealthResponse` (`status`, `version`) |
| GET | `/api/runs/{run_id}/events` | SSE stream of `AgentEvent` ([AGENTS.md](../AGENTS.md#sse-transport)) |
| GET | `/api/runs/{run_id}/graph` | `RunGraph` (static topology for now) |
| GET | `/api/docs`, `/api/openapi.json` | Swagger UI and the OpenAPI schema |

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
