.DEFAULT_GOAL := help

.PHONY: help install dev dev-backend dev-frontend lint fmt typecheck test schema corpus

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install backend + frontend dependencies and the git hooks
	cd backend && uv sync
	cd frontend && pnpm install
	uv run --project backend pre-commit install

dev: ## Run backend (with reload) and frontend dev servers together
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Run the FastAPI backend with auto-reload
	cd backend && BACKEND_RELOAD=true uv run python -m rag_hive

dev-frontend: ## Run the Vite dev server
	cd frontend && pnpm run dev

lint: ## Lint and check formatting (ruff, eslint, prettier)
	cd backend && uv run ruff check . && uv run ruff format --check .
	cd frontend && pnpm run lint && pnpm run format:check

fmt: ## Auto-format everything (writes changes)
	cd backend && uv run ruff check --fix . && uv run ruff format .
	cd frontend && pnpm run format

typecheck: ## Type-check (mypy --strict, tsc)
	cd backend && uv run mypy
	cd frontend && pnpm run typecheck

test: ## Run all tests (pytest, vitest)
	cd backend && uv run pytest
	cd frontend && pnpm test

schema: ## Export the backend wire schema to frontend/src/api/schema.json
	cd backend && uv run python -m rag_hive.schema

corpus: ## Download the corpus PDFs to data/corpus/raw/ and verify their sha256
	cd backend && uv run python -m rag_hive.corpus
