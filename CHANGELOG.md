# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Monorepo scaffold: FastAPI backend with `/health`, the SSE event stream and the workflow
  graph; component interfaces and registries; agent event schema; React dashboard shell with
  placeholder pages; Makefile, pre-commit, CI and contribution docs.

### Changed

- Every backend route now lives under `/api` (`/api/health`, `/api/runs/{run_id}/events`,
  `/api/runs/{run_id}/graph`, docs at `/api/docs`); the dev proxy is a single `/api` rule
  (ADR-004).
- Local-first runtime (ADR-005): Ollama (Qwen) and BGE-M3 via sentence-transformers are the
  only providers, the `anthropic` and `openai` SDKs and API key settings are gone; roadmap
  rewritten around the MSCI benchmark; branch prefixes match the conventional commit types.

### Fixed

- CI backend job: pin `astral-sh/setup-uv` by commit SHA; `@v10` does not resolve.
