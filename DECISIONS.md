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

## ADR-004: Every backend route lives under `/api`

- **Status:** accepted (2026-10-28)
- **Context:** The backend served `/health` and `/runs/{id}/...` at the root, and the frontend
  routes `/runs/:runId/map` and `/runs/:runId/results` share that `/runs` prefix. The Vite
  proxy needed one rule per endpoint plus a regex to keep the app's pages out of it, and a
  single-origin production deploy would hit the same collision on every deep link.
- **Decision:** One `APIRouter(prefix="/api")` mounts every backend router, and FastAPI's
  OpenAPI routes move to `/api/docs` and `/api/openapi.json`. The frontend owns every other
  path. The dev proxy is a single `/api` rule, and the client prefixes each call with
  `API_PREFIX`, checked against the backend's through `schema.json` (ADR-001). A backend test
  fails if any route, OpenAPI path or old root path answers outside `/api`. The endpoint in
  ADR-002 is now `GET /api/runs/{run_id}/events`; its decision is otherwise unchanged.
- **Consequences:** New endpoints need no proxy or deploy changes, and production can serve
  the built app and the API from one origin with one routing rule. Every API URL gets five
  more characters, and anything outside the app that called the old root paths must move to
  `/api`.

## ADR-005: Local-first, no paid API at runtime

- **Status:** accepted (2026-10-28)
- **Context:** The scaffold defaulted to Anthropic for the agents and OpenAI for embeddings,
  so a benchmark run needed API keys and cost money per run. A benchmark that runs every
  parsing × chunking × embedding × retrieval config on several PDFs makes many calls, and
  results that depend on a hosted model's version are hard to reproduce.
- **Decision:** Runtime providers are local only: Ollama (Qwen) for the LLM and BGE-M3 through
  sentence-transformers for embeddings. `Settings` keeps `LLM_PROVIDER` and
  `EMBEDDING_PROVIDER`, and components still go through them (AGENTS.md invariant 4), but the
  only accepted values are `ollama` and `sentence-transformers`. The `anthropic` and `openai`
  SDKs are no longer dependencies. Claude Code is a development tool for working on the repo;
  nothing in `backend/` or `frontend/` calls it.
- **Consequences:** A run costs nothing and works offline once the models are pulled, and
  pinned local models make results reproducible. Setup needs Ollama running and a few GB of
  model downloads; CPU-only machines run slower. Local models grade and generate less well
  than hosted ones, so the Judge's LLM grades need calibration. Adding a hosted provider later
  means a new ADR that supersedes this one.
