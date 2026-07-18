---
trigger: always_on
description: Safety constraints that must never be violated in this codebase
---

# Safety Constraints

## Money & Trading Safety

- **Never enable live/mainnet trading without explicit user instruction.** Default to Sepolia
  testnet and DRY_RUN / paper-trading mode.
- **Never hardcode a mainnet router address** as a fallback for testnet paths — Sepolia and
  mainnet Uniswap router addresses are different contracts.
- **Never remove or weaken risk controls** (position sizing, stop-loss, daily loss cap, slippage
  limit) without explicit direction — note: as of 2026-07-17 none of these exist yet in
  `apps/worker/tasks/analyzer.py`'s analysis→execution path; adding them is planned work, not
  something to skip.
- **Never commit or print a real private key** (`WALLET_PRIVATE_KEY`, `WEB3_WALLET_PRIVATE_KEY`)
  to logs, error messages, or version control.

## Docker & Service Safety

- **Never run `pip install`, `alembic`, or `python` directly on host** — run inside the relevant
  container via `docker compose exec <service> <command>`.
- **Never run destructive Docker commands** (`docker compose down`, image removal, volume prune)
  without explicit user instruction — `scripts/manage_services.sh` already does a `down`/`up`
  cycle on every run, so don't call it casually.
- Compose files are generated per-environment (`docker/environments/{development,staging,production}.yaml`
  + `scripts/generate_compose_file.sh`) — don't hand-edit a generated compose file.

## Secrets & Environment

- **Never commit `env_vars/.env`** — it is gitignored; only `env_vars/.env.example` is tracked.
- **Never hardcode secrets, API keys, or private keys** in source code.
- `WALLET_PRIVATE_KEY`, `WEB3_WALLET_PRIVATE_KEY`, `LLM_API_KEY`, `DISCORD_BOT_TOKEN`, and DB
  credentials must only ever come from environment variables / `Config` (pydantic-settings).

## Database Safety

- **Never delete or modify applied migration files** in `apps/api/alembic/versions/`.
- **Always generate an Alembic migration** after any SQLAlchemy model change under `apps/api/models/`.
- **Never run raw SQL migrations** bypassing Alembic.

## Code Safety

- **Never delete tests** (`apps/worker/tests/`, `apps/api/repositories/tests/`) or weaken coverage
  without explicit direction.
- **Never remove error handling** (try/except, HTTP exceptions) without explicit direction.
- **Never skip ownership/auth checks** on protected API endpoints.
