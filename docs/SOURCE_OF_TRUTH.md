# Cryptobot — Source of Truth

**Last updated: 2026-07-19. This file is the canonical guardrail document for any agent (Devin or otherwise) working in this repo. If something here conflicts with a PR description, an old comment, or your own assumption, this file and the actual code win — re-verify against code before trusting even this document, since it can drift.**

## 0. Rule Zero: Do Not Assume

This project was paused for ~16 months and has accumulated dead code, stale comments, and half-finished features. Do not infer intent from variable names, comments, or README prose alone.

- Before claiming a bug is fixed, a feature exists, or a config value is wired up: **read the actual file**. Do not trust a memory, a prior PR description, or this document's own prose without spot-checking the code it describes.
- If a prompt/issue doesn't specify a behavior (error handling, edge case, naming), **ask**, don't guess. Silent assumptions are the single biggest source of rework in this project's history.
- Every implementation PR is independently audited against its own prompt file (not against the PR's self-description) — see §5. Write code assuming an auditor will re-derive every claim from scratch.

## 1. Project Overview

Cryptobot is an experimental, **not production-ready** Ethereum trading bot. It uses an LLM to analyze market data and decide BUY/SELL/HOLD, then executes trades on-chain via Uniswap. Hendro built this as a hands-on learning project — treat correctness and safety as more important than speed or feature count.

**Current phase:** get the Ethereum path fully working end-to-end on **Sepolia testnet**. Mainnet trading and Solana/other-chain support are explicitly out of scope until Sepolia is proven end-to-end.

**Monorepo layout:**

```
apps/api/       FastAPI + SQLAlchemy + Alembic — REST API (platforms, users, wallets, analysis)
apps/worker/    Celery worker — market data fetch, LLM analysis, trade execution
apps/webapp/    React 19 + Vite + TypeScript — dashboard (minimal scaffold, not wired to API yet)
apps/scrapers/  Data-source scraping helpers
docker/         docker-compose service/environment definitions (generated, not hand-edited)
scripts/        generate_compose_file.sh, manage_services.sh
env_vars/       .env.example (tracked) / .env (gitignored, real secrets)
```

## 2. Current Status (2026-07-19)

Treat this section as a snapshot, not a promise — re-verify against code for anything load-bearing.

**Working / done:**
- Config bugs fixed: `WALLET_PRIVATE_KEY`/`WALLET_ADDRESS`/`DRY_RUN` exist on `Config`; Sepolia Uniswap V2 Router02 address and full ABI populated; `WETH_ADDRESS` is a required config field (no more hardcoded mainnet WETH).
- `EthereumExecutor` (`apps/worker/core/trading/ethereum.py`) BUY and SELL both confirmed working via real signed Sepolia transactions (not just dry-run). SELL sells the actual wallet balance via `balanceOf`, not a hardcoded amount.
- `DRY_RUN` flag exists and gates signing/broadcast in `_execute_buy`, `_execute_sell`, `_approve_token_spending` — defaults to `True`.
- Infra (db/redis/adminer/api via `docker compose -f docker/run-development-compose.yaml`) brings up cleanly; Alembic migrations apply.
- `apps/worker/core/preflight.py` validates wallet/RPC/router config before a live run.
- `MarketDataProvider` interface added (mirrors the `llm/adapters/` pattern): `DexScreenerProvider` and `GeckoTerminalProvider` behind `config.MARKET_DATA_PROVIDER_CLASS`, defaulting to GeckoTerminal because **DexScreener does not index Sepolia testnet pools** (confirmed via direct API checks — this is a hard platform limitation, not a bug to "fix").
- Analyzer → executor wiring: `tasks/analyzer.py`'s `perform_llm_analysis` is being connected to `EthereumExecutor.execute()` — confirm current state by reading `tasks/analyzer.py` directly before relying on this, it has been reworked multiple times (see git log).

**Not working / explicitly out of scope for now:**
- Risk controls — position sizing, stop-loss, daily loss cap, slippage limit — **do not exist anywhere in the pipeline**. Their absence is a known gap, not an oversight to silently work around; adding them is future planned work, not implicit scope of unrelated tasks.
- Full pipeline end-to-end test on Sepolia (analysis → decision → live execution) — in progress, treat as unproven until a real tx hash from Sepolia Etherscan is captured.
- Webapp is not wired to the API.
- Solana / multi-chain support — deferred. Planned via a `base.py` chain-executor interface in `core/trading/` mirroring the LLM adapter pattern, so Ethereum-specific code doesn't get redone later. Do not add chain-specific branching outside `core/trading/`.

**Before starting any task touching `core/trading/`, `config/settings.py`, or `tasks/analyzer.py`: re-read those files first.** They have changed shape several times; don't rely on descriptions above beyond "roughly what to expect."

## 3. Architecture Invariants

- **API** (`apps/api`): models in `apps/api/models/`, DB access only through `apps/api/repositories/` (never raw queries in routes), routes under `/api/v1`. Any SQLAlchemy model change requires a new Alembic migration — never hand-write raw SQL migrations, never edit/delete an already-applied migration file.
- **Worker** (`apps/worker`): Celery app in `main.py`/`bot.py`, tasks in `tasks/`. LLM providers live behind `llm/adapters/` selected via `ADAPTER_CLASS` — new LLM backends must follow this pattern, not add ad-hoc client code. Market data providers likewise live behind `core/market_data_providers/` selected via `MARKET_DATA_PROVIDER_CLASS`. Chain execution lives only in `core/trading/`.
- **Config**: one `pydantic-settings` `Config` class per service (`apps/worker/config/settings.py`, `apps/api` equivalent). Never read `os.environ` directly outside that class. New env-driven values go in `Config` — never a scattered `os.getenv()` call — and must be added to `env_vars/.env.example` and the relevant `docker/services/*.yaml` in the same change.
- **Webapp**: React 19 + Vite + TS, minimal scaffold today — no router/state-manager assumptions without checking `apps/webapp/package.json` first.

## 4. Safety Rules (non-negotiable)

- **Never enable live/mainnet trading without explicit user instruction.** Default to Sepolia + `DRY_RUN=true`.
- **Never hardcode a mainnet address** (router, WETH, or otherwise) as a fallback for a testnet code path.
- **Never weaken or remove risk controls** — moot today since none exist, but once added, don't quietly bypass them.
- **Never commit, log, or print a real private key** (`WALLET_PRIVATE_KEY` or similar). These are `SecretStr` — preserve that typing, never downgrade to `str`.
- **Never commit `env_vars/.env`** — it's gitignored; only `.env.example` is tracked.
- **Docker**: run `pip install`/`alembic`/`python` inside containers (`docker compose exec <service> ...`), never on host. Never run `docker compose down`, image removal, or volume prune without explicit instruction. Compose files under `docker/run-*-compose.yaml` are generated — edit `docker/environments/` or `docker/services/` sources and regenerate via `scripts/generate_compose_file.sh`, don't hand-edit the generated file. `api` hot-reloads; `worker` does not — it needs a restart after code changes.
- **Never delete tests or remove error handling** without explicit direction.

## 5. Implementation Workflow (how work gets done here)

All non-trivial changes go through a staged prompt + audit chain, not a single unreviewed PR:

1. **Implementation prompt** — a self-contained spec (repo, branch name, exact files in scope, acceptance criteria) handed to the Devin coding agent. No dependency on prior chat context.
2. **Audit A1** — independent review checked against the prompt's stated requirements, not the PR's own description. Claims are re-derived from the diff/live behavior, not trusted at face value.
3. **Revision AR1** — only if A1 finds gaps, scoped to exactly the failed items.
4. **Audit A2** — re-checks AR1 items plus a regression spot-check of what A1 already passed.
5. **Final Acceptance Audit (FAA1)** — holistic check of the full cumulative diff before merge.

**Every implementation prompt written for Devin must explicitly instruct Devin to read `docs/SOURCE_OF_TRUTH.md` first, before making any changes, and to defer to it over its own assumptions.** Include a line like: "Before implementing, read `docs/SOURCE_OF_TRUTH.md` in full and follow its rules — do not assume config values, architecture, or scope beyond what it and the code confirm." This applies to every prompt, not just ones that touch areas this doc calls out explicitly.

Rules that follow from this:
- One branch per prompt file, off `main`. Never bundle unrelated fixes into one PR even if they touch the same file.
- Each prompt states an explicit **scope-boundary**: exactly which files may be touched. Touching files outside that boundary is scope creep and gets flagged in audit even if the extra change is itself correct.
- Don't trust a PR description's self-reported "all tests pass" or "verified working" — re-run or re-derive the check.
- Watch for tautological tests that re-implement the logic inline instead of importing and exercising the real function — this is a recurring gap this project's audits catch.
- Draft/planned work items are tracked on the GitHub Projects board (`https://github.com/users/w33ladalah/projects/1`), not just in chat or memory.

## 6. Environment & Config Reference

| File | Purpose |
|---|---|
| `env_vars/.env` | Real values. Gitignored — never commit. |
| `env_vars/.env.example` | Template, tracked in git, no real values. |
| `apps/worker/config/settings.py` | Single source of config truth for the worker (pydantic-settings). |

Key Sepolia-specific values (verify current values in `.env.example`, don't hardcode from memory):
- `INFURA_URL_TESTNET` must point at Sepolia, not Kovan (deprecated) or mainnet.
- `UNISWAP_ROUTER_ADDRESS` must be the Sepolia V2 Router02 address, not mainnet's.
- `WETH_ADDRESS` differs between mainnet and Sepolia — verify against whichever pool is actually being tested, Sepolia WETH deployments can vary.
- `DRY_RUN` defaults to `true`; only flip to `false` with explicit user go-ahead and after a dry-run pass has been exercised.

## 7. Known Platform Limitations (not bugs — don't "fix" these)

- **DexScreener does not index Sepolia testnet pools.** Confirmed via direct API checks, not a query-phrasing issue. This is why `GeckoTerminalProvider` is the default market data provider for testnet work.
- Sepolia WETH/token addresses can vary by faucet or pool — there isn't one canonical address to hardcode.

## 8. Where to Look Before Asking / Assuming

- Repo-local Devin knowledge base (`.devin/` — gitignored, local to Hendro's environment, not visible in a fresh clone): `rules/always-on/`, `rules/worker/known-bugs.md`, `architecture/overview.md`. Treat this file (`docs/SOURCE_OF_TRUTH.md`) as the version that travels with the repo itself.
- Implementation prompts and audit trail: `~/Documents/Work Projects/Cryptobot/Prompts` (outside this repo by design).
- Tracking board: `https://github.com/users/w33ladalah/projects/1`.
- `README.md` in repo root for setup/run instructions.

## Maintenance

This document should be updated whenever: a confirmed bug is fixed, a major architectural decision is made (e.g. a new provider interface), or the current phase/focus changes. Keep it accurate rather than comprehensive — stale specifics are worse than a pointer to "go read the code."
