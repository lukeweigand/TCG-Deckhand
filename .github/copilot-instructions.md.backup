# Copilot instructions for TCG-Deckhand

This repository is currently a fresh scaffold with minimal content. Use these notes to be productive without guessing the stack.

## What exists now
- Files: `README.md` (title only). No source code, no package/dependency manifest, no build/test config.
- Default branch: `main`.
- Environment (from workspace): Windows with PowerShell (`pwsh`) as the default shell.

## Operating assumptions for agents
- Do not introduce a tech stack or dependencies unless the user explicitly requests scaffolding or confirms choices.
- Prefer minimal, incremental PRs; clearly summarize decisions and add quickstart notes to `README.md` when creating runnable code.
- Format any example commands for PowerShell, not Bash.

## PowerShell command conventions (important)
- Use `$env:VAR = 'value'` (not `VAR=value`) for env vars.
- Use backtick `` ` `` for line continuations when needed.
- Prefer cross-platform CLI flags; avoid Bashisms (e.g., `&&` chains can be used, but avoid `export`, process substitution, etc.).

## When the user asks to scaffold the project
- Confirm goals: app type (CLI/GUI/web/service), language, package manager, and minimal feature set.
- Create a minimal, runnable baseline with:
  - A dependency manifest and lockfile (e.g., `package.json`/`pnpm-lock.yaml`, `pyproject.toml`, etc.).
  - A tiny smoke test and a simple run/build script (package scripts or `.vscode/tasks.json`).
  - Updated `README.md` with “How to run”, “How to test”, and any required environment variables.
- Keep initial structure small (e.g., `src/`, `tests/`, and configuration files only as needed).

## Documentation and workflows
- Record any non-obvious commands (build, run, test, lint) in `README.md` as you introduce them.
- If you add automation, include a short explanation and the exact PowerShell command users should run.
- Keep this file (`.github/copilot-instructions.md`) updated to reflect real, committed patterns—avoid aspirational guidance.

## What to clarify with the maintainer (before big changes)
- Project purpose and target users for “TCG-Deckhand”.
- Preferred language/framework and package manager.
- Testing expectations (unit only vs. integration), and CI (if any).
- Any constraints (offline-only, no external services, licensing, etc.).

## Example next safe step
- Propose 1–2 concrete scaffolding options (e.g., “TypeScript CLI” vs “Python CLI”) with a short trade-off note and PowerShell setup commands. Wait for approval before creating files.
