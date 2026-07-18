---
trigger: always_on
description: Architectural invariants that must hold across all layers of the system
---

# Architecture Invariants

These structural rules must hold true across all code changes.

## API Invariants (`apps/api`)

- **Models** live in `apps/api/models/` (`analysis.py`, `platform.py`, `token.py`, `token_pair.py`,
  `users.py`, `wallet.py`) and are exported from `apps/api/models/__init__.py`.
- **Repositories** wrap DB access (`apps/api/repositories/`) — routes should not query the DB directly.
- **Routes** live in `apps/api/routes/` and are mounted under `/api/v1` (see `apps/api/routes/__init__.py`).
- **Any SQLAlchemy model change** requires a new Alembic migration in `apps/api/alembic/`.
- **Config/settings** flow through `pydantic-settings`; never read `os.environ` directly in route/repo code.

## Worker Invariants (`apps/worker`)

- **Celery app** is defined in `apps/worker/main.py` / `bot.py`; tasks live in `apps/worker/tasks/`.
- **LLM adapters** live in `apps/worker/llm/adapters/` behind a common interface
  (`ADAPTER_CLASS` config selects which one) — new LLM providers must follow this pattern, not
  bypass it with ad-hoc client code.
- **Chain execution** lives in `apps/worker/core/trading/` (currently `ethereum.py` only). The
  planned multi-chain design mirrors the LLM adapter pattern: a `base.py` executor interface with
  per-chain implementations. Don't add chain-specific logic outside `core/trading/` — see
  `rules/worker/known-bugs.md` for the current state of `ethereum.py`.
- **Config** is a single `pydantic-settings` `Config` class in `apps/worker/config/settings.py` —
  add new env-driven values there, not as scattered `os.getenv()` calls.
- **Analysis → execution pipeline**: `tasks/analyzer.py`'s `perform_llm_analysis` produces a
  BUY/SELL/HOLD decision. As of 2026-07-17 this is **not wired** to `EthereumExecutor` and there
  are **no risk controls** (position sizing, stop-loss, daily loss cap, slippage limit) anywhere
  in the pipeline — do not treat their absence as intentional; it's open work.

## Webapp Invariants (`apps/webapp`)

- React 19 + Vite + TypeScript, currently a minimal scaffold (`App.tsx`, `main.tsx`) — no Redux,
  routing, or API client wired up yet. Don't assume conventions (e.g. a specific state manager)
  that aren't in the code; check `apps/webapp/package.json` before adding a dependency.

## Environment/Config Invariant

Env vars are defined in `env_vars/.env.example` and consumed differently per service (see
`docker/services/*.yaml` for the mapping) — e.g. the worker maps `OPENROUTER_*` vars to generic
`LLM_API_KEY`/`LLM_BASE_URL`/`MODEL_NAME` config keys. When adding a new env var, update
`.env.example`, the relevant `docker/services/*.yaml`, and the `Config` class together.
