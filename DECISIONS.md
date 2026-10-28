# Decisions

Short architecture decision records. Add new entries at the bottom; never rewrite accepted
ones, supersede them instead.

## ADR-001: Backend Pydantic models own the wire format

- **Status:** accepted (2026-10-28)
- **Context:** The backend (Python) and frontend (TypeScript) share event, graph and health
  types. Generating TS from JSON Schema needs another toolchain; hand-written mirrors drift.
- **Decision:** Pydantic models extending `WireModel` are the source of truth. `make schema`
  exports their JSON Schema to `frontend/src/api/schema.json` (committed). The TS types are
  written by hand; a backend test fails when the committed schema is stale, and a frontend test
  checks the TS enums (event types, agent names, edge kinds) against it.
- **Consequences:** Readable, TSDoc'd TS types and no extra dependency. A field added on one
  side only is caught for enums but not yet for every field; revisit with codegen if drift bites.

## ADR-002: SSE with `seq` ids for the event stream

- **Status:** accepted (2026-10-28)
- **Context:** The dashboard needs a one-way, ordered, live stream of agent events that
  survives reconnects. WebSockets are bidirectional and need their own resume logic.
- **Decision:** `GET /runs/{run_id}/events` streams SSE. Each frame's `id` is the event's
  per-run `seq` and its `event` name is the event `type`. On reconnect the browser sends
  `Last-Event-ID`; the source may use it to replay, and the endpoint drops anything at or
  below it regardless. Implemented with `StreamingResponse`, no SSE library.
- **Consequences:** Native `EventSource` reconnects for free. Event sources must assign
  strictly increasing `seq` per run and be able to replay from an offset.

## ADR-003: Async component interfaces behind name registries

- **Status:** accepted (2026-10-28)
- **Context:** The Planner must combine any parser, chunker, embedder and retriever from a
  config, and several of them (API parsers, semantic chunkers, API embedders) do I/O.
- **Decision:** Each kind has one ABC with async methods and one `Registry[T]`. Implementations
  declare a stable `name` and a frozen Pydantic `config_model`, and register with a decorator.
  `registry.create(name, config)` validates the config and builds the instance.
- **Consequences:** CPU-bound implementations must offload work (`asyncio.to_thread`) to keep
  the event loop free. Registry names appear in benchmark results, so renaming one is a
  breaking change.
