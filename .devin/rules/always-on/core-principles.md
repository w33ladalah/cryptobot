---
trigger: always_on
description: Critical engineering principles that apply to every change in this codebase
---

# Core Engineering Principles — Crypto Bot

Crypto Bot is an experimental, **not-yet-fully-working** Ethereum trading bot. It uses an LLM
to analyze market data (CoinGecko + DexScreener) and decide BUY/SELL/HOLD, executing trades
on-chain via Uniswap. Hendro built this to learn crypto hands-on — treat it as an active
learning project, not a hardened production system.

## Project Root
`/Users/hendrowibowo/Projects/cryptobot`

## Monorepo Structure
```
apps/api/       → FastAPI + SQLAlchemy + Alembic (Python) — REST API for platforms, users, wallets, analysis results
apps/worker/    → Celery worker (Python) — market data fetch, LLM analysis, trade execution
apps/webapp/    → React 19 + Vite + TypeScript — dashboard for monitoring the bot
apps/scrapers/  → data-source scraping helpers
docker/         → docker-compose service/environment definitions
scripts/        → generate_compose_file.sh, manage_services.sh
```

## Current Focus

Getting the **Ethereum path working end-to-end on Sepolia testnet** before anything else.
Solana/other-chain support is deliberately deferred to a later phase, planned via a
`base.py` chain-executor-interface abstraction (mirroring the existing `apps/worker/llm/adapters/`
pattern) so Ethereum-specific work won't need redoing.

Known confirmed bugs blocking this are tracked in `rules/worker/known-bugs.md` — check it
before touching `apps/worker/core/trading/` or `apps/worker/tasks/analyzer.py`.

## Non-Negotiable Rules

1. **Minimal changes** — fix what's asked, don't broad-refactor unless requested.
2. **Root cause fixes** — fix upstream (e.g. `config/settings.py`), never patch around a bug downstream.
3. **Imports at top** — never mid-file imports (unless circular import forces lazy import).
4. **No emoji in code** unless user explicitly requests.
5. **Preserve existing code style** in every file touched.
6. **Never add/remove comments** unless explicitly asked.
7. **Ask user to verify** before suggesting a git commit.
8. **Real money is at stake once this leaves testnet** — no trade-execution change ships without
   an explicit DRY_RUN / paper-trading path being exercised first. See `rules/always-on/safety.md`.
