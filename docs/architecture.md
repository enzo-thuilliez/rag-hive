# Architecture

## Components

```text
frontend (Vite dev server :5173)          backend (uvicorn :8000)
┌──────────────────────────────┐          ┌───────────────────────────────────────┐
│ pages: Upload, Agent Map,    │          │ api/ (router, prefix /api)            │
│        Results               │  /api/*  │   health.py                           │
│ api/client.ts                │ ───────► │   runs.py ── events/source.py         │
│ api/events.ts, api/graph.ts  │          │    │         (RunEventSource)         │
└──────────────────────────────┘  (proxy) │    └── agents/graph.py                │
                                          │ agents/ (LangGraph workflow, stubs)   │
                                          │   uses llm/ parsers/ chunkers/        │
                                          │        embedders/ retrievers/         │
                                          │        corpus/ evaluation/            │
                                          └───────────────────────────────────────┘
```

Every backend route, the OpenAPI docs included, lives under `/api`; every other path belongs to
the frontend ([ADR-004](../DECISIONS.md#adr-004-every-backend-route-lives-under-api)). In dev,
Vite proxies `/api` to the backend, so the browser stays same-origin. In production the same
split lets one origin serve both. Ports and hosts come from the root `.env`.

## Module map

Every module below exists. Those marked *stub* have their models, signatures and docstring
contracts in place but bodies that raise `NotImplementedError`; their interfaces are frozen
([ADR-006](../DECISIONS.md#adr-006-interfaces-are-frozen-early-changing-one-takes-a-new-adr)).

| Module (`backend/src/rag_hive/`) | Role | State |
| --- | --- | --- |
| `config.py` | `Settings`: every tunable value, from env / `.env` | real |
| `core/wire.py`, `core/data.py` | `WireModel` (camelCase, frontend) and `DataModel` (snake_case, files and agent state) | real |
| `core/models.py` | `ParsedDocument`, `Chunk`, `ScoredChunk`: data between pipeline stages | real |
| `core/component.py`, `core/registry.py` | `Component` base and name → class `Registry` | real |
| `parsers/`, `chunkers/`, `retrievers/` | async ABC + registry each | interfaces, no implementation |
| `embedders/` | `Embedder` ABC + registry; `sentence_transformer.py`, BGE-M3 by default | stub |
| `llm/` | `LLMProvider` ABC, `llm_registry`, `create_llm`; `ollama.py` is the only provider | stub |
| `agents/profiler.py` … `agents/reporter.py` | per agent: input model, output model, `run_*`, LangGraph node | stub |
| `agents/state.py` | `WorkflowState`, the LangGraph state | real |
| `agents/graph.py` | topology table, `build_workflow` (`StateGraph`), `build_run_graph` (dashboard) | real, except `fan_out_workers` |
| `agents/topology.py` | `RunGraph` wire types | real |
| `events/` | `AgentEvent` schema, SSE framing, `RunEventSource` | real (empty source) |
| `corpus/models.py` | `CorpusEntry`, `CorpusManifest`, `DocumentProperties` | real |
| `corpus/manifest.py`, `corpus/download.py`, `corpus/derive.py`, `corpus/__main__.py` | manifest loading, checksum-verified download, image-only derived files, `make corpus` | real |
| `evaluation/golden.py` | `GoldenQuestion`, `ExpectedPassage` (validated), golden set loading | model real, loader stub |
| `evaluation/span_matching.py` | which retrieved chunks cover which expected passages | stub |
| `evaluation/metrics/retrieval.py` | recall@k, hit rate@k, MRR, nDCG@k, `RetrievalScores` | stub |
| `evaluation/metrics/parsing.py` | normalized edit distance, TEDS | stub |
| `api/` | the `/api` router | real |
| `schema.py` | `make schema`: wire schema to the frontend, data schemas to `docs/schemas/` | real |

### Workflow data flow

```text
WorkflowState(run_id, document_id, pdf_path, ks, golden_set)
  → profiler      reads ProfilerInput      writes profile: DocumentProfile
  → planner       reads PlannerInput       writes plan: Plan (PipelineConfig list)
  → qa_generator  reads QAGeneratorInput   writes question_set: QuestionSet (GoldenQuestion list)
  → worker × N    gets WorkerInput (Send)  appends worker_outputs: WorkerOutput
  → judge         reads JudgeInput         writes scores: Scores (RetrievalScores per config)
  → reporter      reads ReporterInput      writes report: Report
```

Each node receives only its input model (LangGraph `input_schema`) and returns only the keys it
writes, so agent modules never import `WorkflowState`.

### Evaluation without chunk labels

The golden set stores expected passages as verbatim text with a page, not chunk ids.
`span_matching.match_spans` decides which retrieved chunks cover which passages, and the
retrieval metrics work on that coverage, so every chunker is scored against the same labels.

### Data schemas

`make schema` writes `docs/schemas/corpus-entry.schema.json`, `corpus-manifest.schema.json` and
`golden-question.schema.json` from the Pydantic models, for editors and other tools that
validate the corpus manifest and golden sets. A test fails if they are stale.

### Corpus

`data/corpus/manifest.yaml` (committed) pins each PDF by SHA-256; the PDFs live in
`data/corpus/raw/<id>.pdf` (gitignored, never committed). `make corpus` handles each entry:

| Entry | File present, checksum matches | File present, wrong checksum | File missing |
| --- | --- | --- | --- |
| `auto` | kept | downloaded again | downloaded, kept only if the checksum matches |
| `manual`, pinned | kept | error | instructions printed, error |
| `manual`, `sha256: ""` | error, prints the file's checksum to pin | same | instructions printed, error |

`derived` entries come after their sources. `make corpus` renders the source's selected pages
(`page_range`) into an image-only PDF in `data/corpus/derived/<id>.pdf` (gitignored), with
pypdfium2 for rendering and Pillow for writing. A derived file has no pinned checksum, since its
bytes depend on the rasterizer's version. Instead it records its source checksum, pages and dpi
in its PDF `Keywords`, and it is generated again whenever that record no longer matches the
manifest. It fails if its source is missing or does not match its pin.

It exits 1 if any entry is not ready. Downloads go to a temporary file first, so a failed or
mismatched download never leaves a file under the final name. CI validates the manifest
against `CorpusManifest` (`tests/test_corpus_manifest.py`) and never downloads.

## Endpoints

| Method | Path | Returns |
| --- | --- | --- |
| GET | `/api/health` | `HealthResponse` (`status`, `version`) |
| GET | `/api/runs/{run_id}/events` | SSE stream of `AgentEvent` ([AGENTS.md](../AGENTS.md#sse-transport)) |
| GET | `/api/runs/{run_id}/graph` | `RunGraph` (static topology for now) |
| GET | `/api/docs`, `/api/openapi.json` | Swagger UI and the OpenAPI schema |

## Event stream

The endpoint reads from a `RunEventSource` (a FastAPI dependency). The default
`EmptyEventSource` yields nothing, so the stream closes immediately. The agents step replaces it with
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
