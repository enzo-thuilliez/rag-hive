# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-11-07)


### Features

* **backend:** download and verify the corpus with make corpus ([02164b0](https://github.com/enzo-thuilliez/rag-hive/commit/02164b0b01573af7e7e2ed3ca4dba667a1955219))
* **corpus:** pin manual entries, FRASER page range and image-only variant ([#54](https://github.com/enzo-thuilliez/rag-hive/issues/54)) ([69749ff](https://github.com/enzo-thuilliez/rag-hive/commit/69749ffcd6bb2294d7a2013a077fc4dd7aa652dc))
* pinned corpus manifest and make corpus ([02e7790](https://github.com/enzo-thuilliez/rag-hive/commit/02e7790baa96d64f284642d269de1560122bc61f))
* **repo:** pin the 10 corpus documents in the manifest ([c249e9c](https://github.com/enzo-thuilliez/rag-hive/commit/c249e9c139fb8dd104d8077a3bc923e572dcf901))


### Bug Fixes

* **ci:** pin setup-uv by commit sha ([cdf4aba](https://github.com/enzo-thuilliez/rag-hive/commit/cdf4aba0b459d8f1befed7b81efba9a031c0db4e))
* **ci:** pin setup-uv by commit sha ([be499c4](https://github.com/enzo-thuilliez/rag-hive/commit/be499c4d7fe13cf9fecd23f83a945616efc09a67))

## [Unreleased]

### Added

- Monorepo scaffold: FastAPI backend with `/health`, the SSE event stream and the workflow
  graph; component interfaces and registries; agent event schema; React dashboard shell with
  placeholder pages; Makefile, pre-commit, CI and contribution docs.
- Typed stubs for every planned module (ADR-006): the six agents with input/output models and
  LangGraph nodes, the workflow graph that also serves `/api/runs/{run_id}/graph`, the Ollama
  LLM provider, the BGE-M3 embedder, `CorpusEntry`, `GoldenQuestion`, span matching and the
  retrieval and parsing metrics. `make schema` also exports the corpus and golden question
  schemas to `docs/schemas/`.
- Corpus: `data/corpus/manifest.yaml` pins 10 benchmark PDFs by URL and SHA-256, and
  `make corpus` downloads them to `data/corpus/raw/` (never committed), verifies every checksum
  and prints instructions for gated documents marked `download: manual` (ADR-007).
- Corpus page ranges and derived files (ADR-008): the 1920 Federal Reserve report is cut to 40
  representative pages, and `make corpus` generates an image-only copy of them with no text
  layer into `data/corpus/derived/`, so OCR parsers face a true scan.
- Corpus pinned: the NVIDIA 10-Q, the TotalEnergies URD and the three French Amundi documents
  (factsheet, DIC, prospectus) now carry their SHA-256, pages and properties, so `make corpus`
  verifies all 10 documents and the roadmap's Corpus step is done.

### Changed

- Dependabot groups take minor and patch bumps only; majors come as separate PRs, and
  TypeScript stays below 6.1 until typescript-eslint supports it.
- CI runs on `ubuntu-24.04` with every action pinned to a commit SHA; `dependabot.yml` opens
  weekly grouped updates for GitHub Actions, uv and npm.
- Workflow docs: issue → branch → PR with `Closes #N` → squash merge, `type:*`, `area:*` and
  `priority:*` labels plus a milestone on every issue, docs-only changes in their own PR,
  `corpus` commit scope; issue templates use the new labels.
- Every backend route now lives under `/api` (`/api/health`, `/api/runs/{run_id}/events`,
  `/api/runs/{run_id}/graph`, docs at `/api/docs`); the dev proxy is a single `/api` rule
  (ADR-004).
- Local-first runtime (ADR-005): Ollama (Qwen) and BGE-M3 via sentence-transformers are the
  only providers, the `anthropic` and `openai` SDKs and API key settings are gone; roadmap
  rewritten around the MSCI benchmark; branch prefixes match the conventional commit types.

### Fixed

- CI backend job: pin `astral-sh/setup-uv` by commit SHA; `@v10` does not resolve.
