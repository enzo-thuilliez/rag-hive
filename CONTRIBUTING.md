# Contributing to RAG Hive

Coding agents: the same rules, written for you, are in
[AGENTS.md](AGENTS.md#workflow-for-coding-agents).

## Setup (WSL / Linux)

You need Python 3.12 with `uv`, Node 24 with pnpm, and `make`.

```sh
# Python (uv installs Python 3.12 itself, from .python-version)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node 24 + pnpm (via nvm and corepack; versions from .nvmrc and package.json)
nvm install
corepack enable pnpm
```

Then:

```sh
git clone git@github.com:enzo-thuilliez/rag-hive.git
cd rag-hive
cp .env.example .env
make install
```

## Scripts

| Command | What it does |
| --- | --- |
| `make install` | `uv sync`, `pnpm install`, `pre-commit install` (pre-commit + commit-msg) |
| `make dev` | Backend (uvicorn, reload) and Vite dev server together |
| `make lint` | ruff check + format check, ESLint, Prettier check |
| `make fmt` | ruff fix + format, Prettier (writes changes) |
| `make typecheck` | `mypy --strict`, `tsc -b` |
| `make test` | pytest, Vitest |
| `make schema` | Regenerate `frontend/src/api/schema.json` from the backend |
| `make help` | List every target |

CI runs the backend job (ruff, mypy, pytest) and the frontend job (ESLint, Prettier, tsc,
Vitest, build) on every push to `main` and every PR. `ci-pass` is the required check.

## Workflow

1. Pick an issue, or open one with the Feature or Bug template. Read the issues listed under
   its Dependencies; if one is still open, the issue isn't ready. Every issue has one `type:*`
   label, one or more `area:*` labels, one `priority:p0|p1|p2` label and the milestone of its
   [roadmap](ROADMAP.md) step.
2. Branch from `main` as `<type>/<short-slug>`, where `<type>` is the conventional commit type
   of the change: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf` or `ci`. One
   issue, one branch, one PR.
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/):
   `type(scope): lowercase summary`, e.g. `feat(backend): add pymupdf parser`.
   Scopes: `backend`, `frontend`, `agents`, `events`, `eval`, `corpus`, `docs`, `ci`, `deps`,
   `repo`.
4. Add one bullet under `Unreleased` in [CHANGELOG.md](CHANGELOG.md), in its own last commit.
   Never edit existing bullets.
5. Before pushing: `make lint`, `make typecheck`, `make test`.
6. Open a PR against `main` using the template. Its first line is `Closes #N` (or
   `Part of #N` when the PR is one step of the issue).
7. If `main` moved, merge it into your branch. Never rebase, never force push.
8. Once CI is green, the product owner squash-merges (the only merge method; the PR title
   becomes the commit message). Nobody pushes to `main` directly: a ruleset requires a PR and
   the `ci-pass` check, and blocks force pushes and branch deletion.

Docs-only changes go in their own small PR, never mixed into a code PR.

## Using Claude Code

The repo ships project permissions in `.claude/settings.json`. Claude Code ignores their
allow rules until you trust the workspace: run `claude` once in the repo and accept the
trust dialog. Deny rules (no recursive force deletes, no force pushes, no pushes to `main`)
apply either way.

## Docs to keep in sync

- [AGENTS.md](AGENTS.md) when the agent or event contract changes, in the same PR.
- `frontend/src/api/` and `schema.json` (`make schema`) when a backend wire type changes.
- [DECISIONS.md](DECISIONS.md) for decisions with trade-offs (add an ADR).
- [CHANGELOG.md](CHANGELOG.md) under `Unreleased` for every PR.
- [ROADMAP.md](ROADMAP.md) when a PR completes a roadmap item (move it to `Done`).
