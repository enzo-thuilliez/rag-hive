# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Changed

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
