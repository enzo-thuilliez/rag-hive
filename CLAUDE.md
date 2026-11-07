@AGENTS.md

## Claude Code notes

- `.claude/settings.json` allows the uv/pnpm/make commands, local git, `git push -u origin` for
  `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`, `perf/` and `ci/` branches (one per
  conventional commit type), `gh issue create`, `gh pr create` and reading PR checks. Pushes to
  `main`, force pushes, `gh pr merge` and `rm -rf` are denied.
- Project allow rules only load once the workspace is trusted: run `claude` interactively in
  the repo and accept the trust dialog. Until then only the deny rules apply.
- Claude Code is a dev tool here, not a runtime dependency (ADR-005).
