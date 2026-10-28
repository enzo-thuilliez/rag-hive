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

## ADR-006: Interfaces are frozen early; changing one takes a new ADR

- **Status:** accepted (2026-10-28)
- **Context:** The pipeline components, the LLM provider, the agents, the corpus manifest and
  the evaluation code will be filled in over many PRs, often by coding agents working in
  parallel. If each PR adjusts the interfaces it touches, the pieces stop fitting together and
  benchmark results stop being comparable across PRs.
- **Decision:** Every planned module exists now as a typed stub: Pydantic models, ABCs and
  function signatures with Google-style docstrings stating the contract, and bodies that raise
  `NotImplementedError`. Those signatures, model fields and docstring contracts are frozen.
  An implementation PR fills in bodies and may add private helpers, new registered
  implementations, or optional config fields with defaults. Removing or renaming a field,
  changing a signature or a documented behaviour (a metric's definition, a model's
  validation rule) needs a new ADR in the same PR that says what changes and why, and the
  matching update to AGENTS.md, `make schema` output and tests.
- **Consequences:** Implementation PRs stay small and parallel, and the architecture is
  readable before it works. A wrong early guess costs an ADR rather than a quiet edit, which is
  the point: the change is recorded. Stubs that turn out to be unneeded are removed the same
  way.

## ADR-007: Manual downloads for gated corpus documents

- **Status:** accepted (2026-10-29). Amends the `CorpusEntry` interface frozen by ADR-006.
- **Context:** Some corpus documents cannot be fetched by a script without getting around a
  gate: Amundi's ETF documents sit behind an investor-profile disclaimer, totalenergies.com
  answers automated requests with 403, and NVIDIA's 10-Q has no direct PDF link. Working
  around a gate is not acceptable, but those documents (French text, fund factsheets, KIDs)
  are part of what the benchmark has to cover.
- **Decision:** `CorpusEntry` gets `download: auto | manual`. An `auto` entry needs `url` and
  `sha256`. A `manual` entry has no `url`; it needs `source_page` and a one-line
  `instructions`, and may leave `sha256` empty until a person has downloaded and inspected the
  file. `pages` and `properties` become optional and are required once `sha256` is set. The
  manifest file is a `CorpusManifest` (`documents`, unique ids). `ensure_document` takes the
  HTTP client as a keyword argument (so tests mock it) and returns whether it downloaded. For
  manual entries, `make corpus` only verifies a file a person saved under the expected name,
  prints the instructions for every missing one, and exits non-zero. The
  `DocumentProperties.scanned` description now says "scanned images, any text layer from OCR",
  since most public scans carry an OCR layer.
- **Consequences:** Every corpus document is still pinned by checksum, and nothing is fetched
  in a way the publisher blocks. A fresh clone cannot reach a complete corpus with one command:
  someone downloads the manual files once, and benchmarks that need them fail loudly until
  then. Unpinned manual entries are visible in the manifest (`sha256: ""`) and in
  `make corpus` output.

## ADR-008: Page ranges and derived image-only corpus files

- **Status:** accepted (2026-10-29). Amends the `CorpusEntry` interface (ADR-006, ADR-007).
- **Context:** The 1920 Federal Reserve report has 645 pages, far more than a benchmark run
  needs, and its scan carries a 2009 OCR text layer, so text-layer parsers read that old OCR
  and never face a real scan. Comparing OCR parsers needs the same pages with no text layer at
  all. That file cannot be downloaded from anywhere; it has to be generated, and committing it
  is out of the question (redistribution rights, as for every corpus PDF).
- **Decision:** `CorpusEntry` gets an optional `page_range` (`"20-31,141-154,163-176"`:
  1-based, inclusive, ascending, disjoint, within `pages`). The pinned file stays whole; the
  benchmark uses only the selected pages (`CorpusEntry.selected_pages()`). A third mode,
  `download: derived`, with a `derivation` (`kind: image_only`, `source`, `dpi`), describes a
  file that `make corpus` generates into `data/corpus/derived/` from its source's selected
  pages: grayscale renders, one JPEG image per page, no text, fonts or vector content. A
  derived entry has no `sha256`, since its bytes depend on the pypdfium2 and Pillow versions.
  Instead the file stores a record of its source checksum, pages and dpi in its PDF
  `Keywords` and is regenerated when the record differs. It declares `pages` (validated
  against its source's selection) and `properties`, and no `page_range` of its own.
  `sha256` now defaults to empty. `sync_corpus` takes the derived directory, and
  `ensure_document` refuses derived entries.
- **Consequences:** The FRASER report costs 40 pages of benchmark time instead of 645, and OCR
  parsers can be compared on a true scan of the same pages a text-layer parser reads. Derived
  files are reproducible from pinned sources but not byte-identical across library versions,
  so results that depend on their exact pixels name the library versions from `uv.lock`.
  pypdfium2 and Pillow become runtime dependencies (permissive licenses; PyMuPDF, AGPL, was
  avoided).
