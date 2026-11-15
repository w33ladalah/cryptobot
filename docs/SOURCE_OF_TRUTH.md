# Cryptobot — Source of Truth

**Last updated: 2026-11-15. This file is the canonical guardrail document for any agent (Devin or otherwise) working in this repo. If something here conflicts with a PR description, an old comment, or your own assumption, this file and the actual code win — re-verify against code before trusting even this document, since it can drift.**

## 0. Rule Zero: Do Not Assume

This project was paused for ~16 months and has accumulated dead code, stale comments, and half-finished features. Do not infer intent from variable names, comments, or README prose alone.

- Before claiming a bug is fixed, a feature exists, or a config value is wired up: **read the actual file**. Do not trust a memory, a prior PR description, or this document's own prose without spot-checking the code it describes.
- If a prompt/issue doesn't specify a behavior (error handling, edge case, naming), **ask**, don't guess. Silent assumptions are the single biggest source of rework in this project's history.
- Every implementation PR is independently audited against its own prompt file (not against the PR's self-description) — see §5. Write code assuming an auditor will re-derive every claim from scratch.

## 1. Project Overview

Cryptobot is an experimental, **not production-ready** Ethereum trading bot. It uses an LLM to analyze market data and decide BUY/SELL/HOLD, then executes trades on-chain via Uniswap. Hendro built this as a hands-on learning project — treat correctness and safety as more important than speed or feature count.

**Current phase:** get the Ethereum path fully working end-to-end on **Sepolia testnet**. Mainnet trading and Solana/other-chain support are explicitly out of scope until Sepolia is proven end-to-end.

**Monorepo layout:**

```text
apps/api/       FastAPI + SQLAlchemy + Alembic — REST API (platforms, users, wallets, analysis)
apps/worker/    Celery worker — market data fetch, LLM analysis, trade execution
apps/webapp/    React 19 + Vite + TypeScript — dashboard (minimal scaffold, not wired to API yet)
apps/scrapers/  Data-source scraping helpers
docker/         docker-compose service/environment definitions (generated, not hand-edited)
scripts/        generate_compose_file.sh, manage_services.sh
env_vars/       .env.example (tracked) / .env (gitignored, real secrets)
```

### Goal and development path

**Goal:** learn first (crypto, on-chain execution, bot design), then test whether the bot can earn money. Earning is a hypothesis to be tested with evidence, not an assumption. Testnet token prices have no economic meaning, so Sepolia work proves the plumbing, not profitability.

**Approach:** build the bot in this repo and keep the scope narrow. Own the distinctive parts (LLM analysis, on-chain Uniswap execution, the data pipeline) and the essentials (scheduler, stored signals and trades, basic risk exits). Borrow patterns from Freqtrade (dry-run, persistence, risk exits, Telegram, dashboard) and Hummingbot (DEX connectors) instead of reinventing their designs. If a later piece is not worth building (for example backtesting), adopt a proven tool for it then. Evaluating Hummingbot or Freqtrade is optional and must not block any milestone.

**Design requirements (apply to every milestone below):** these keep later features cheap to add.

1. **Strategy interface.** A strategy takes market data and returns a signal (decision plus reasoning). It never touches the wallet or the executor. The current LLM logic becomes the first strategy; rule-based strategies (indicator rules, DCA) plug in later behind the same interface, mirroring the `llm/adapters/` pattern.
2. **Pure-function strategies.** A strategy's output depends only on its input data, so the same code can later be replayed over historical data for backtesting.
3. **Executor interface.** `core/trading/base.py` defines the chain/venue executor interface (already planned for Solana). A second venue means a second executor, with no change to strategy code.
4. **Record inputs from day one.** Every signal stores its input snapshot, model name, prompt version and raw LLM response. This history cannot be recovered later and is the evidence for the mainnet gate.

### Milestones

Milestones are ordered and each depends on the one before it.

- **M0: finish the current plumbing.**
  - Issue #41: `OpenAiAdapter` sends an `x-opencode-session` header and a `cryptobot-worker/0.1` user agent when the base URL host is `opencode.ai`; default model becomes `deepseek-v4.1-flash`; tests added.
  - Issue #24: a dry-run pass, then a live Sepolia pass, through `perform_llm_analysis`, with the real tx hash captured from Sepolia Etherscan. Dry-run results, mocked decisions, and scripts that bypass `perform_llm_analysis` do not count.
- **M1: autonomous, recorded, guarded.**
  1. Celery beat scheduler (hourly default, configurable). Retire the stub in `apps/worker/bot.py` and the commented-out beat block in `main.py`.
  2. One decision per token per run: select a single pool (for example the highest-liquidity one) instead of trading inside the per-pool loop.
  3. Split analysis from execution: strategy produces a signal, the signal is persisted, guardrails run, then the executor trades. Introduce the strategy interface and the executor interface here.
  4. Persistence via an Alembic migration, written directly by the worker using shared models: `worker_runs` (status, start/end, error), `signals` (decision, reasoning, model, prompt version, raw response, input snapshot), `trades` (signal link, side, amounts, tx hash, status, `dry_run` flag, network).
  5. Minimal guardrails: pause flag read at the start of each run, run lock so runs cannot overlap, cooldown after a trade, maximum position and trade size, position awareness (no SELL with zero balance, no BUY above the cap).
  6. LLM hardening: temperature, timeout and max tokens set in the adapter; raw response stored with each signal.
- **M2: visible.**
  1. Auth on the new endpoints using the existing JWT helpers (`apps/api/utils/jwt.py`). Analysis endpoints that start tasks move from GET to POST and require `network`.
  2. Read-only endpoints: worker status (last run, next run, paused or not), signals, trades, wallet balance (read on-chain from the public address only), trend data.
  3. Frontend replaces the scaffold: worker status, signals with reasoning, wallet balance, trend chart, trade history with Etherscan links. Polling, no websockets.
- **M3: controllable.** Authenticated pause, resume, stop-new-entries and run-now endpoints. `DRY_RUN` stays an environment setting only and is never toggled through the API.
- **M4: strategy parity (before any mainnet use).**
  1. Risk exits: stop-loss, take-profit and trailing stop. These need a separate, cheap, frequent price-check task, independent of the slower LLM analysis task.
  2. Token whitelist and blacklist beyond the address allowlist.
  3. Telegram notifications and basic remote control (status, profit, balance, pause).
  4. Performance metrics: PnL, win rate, drawdown, including fees and gas.
  5. Rule-based strategies (indicator rules, DCA) behind the strategy interface, and multi-token runs.
- **M5: mainnet gate (requires explicit instruction from Hendro at each step).**
  1. Slippage protection: a nonzero minimum output on swaps. `swapExactETHForTokens` currently passes 0 on BUY; the SELL path has not been reviewed for the same problem. Plus full risk controls: daily loss cap and slippage limit.
  2. Paper trading against real mainnet prices for several weeks, with signals and simulated trades stored.
  3. Compare the result with simply holding, after fees and gas. Hendro sets the pass criteria before the run starts.
  4. Only if the gate passes: small real funds in a dedicated hot wallet holding only an amount that can be lost.

**Decisions recorded (Hendro, 2026-11-15):**

- The MVP is complete after M0, M1 and M2. M3 is the first follow-up.
- The worker writes to the database directly using shared models, not through an API endpoint.
- Build in this repo with a narrow scope; adopting an outside framework is optional and later.

**Deferred (not scheduled):** backtesting (build or adopt a tool later; it depends on the stored historical data from M1), grid bots, multi-exchange support (a new executor), more DEXs or chains including Solana, arbitrage and market making, and wider LLM roles (risk flags from news, a veto-only critic, regime labels, explanations, shadow mode).

## 2. Current Status (2026-11-15)

Treat this section as a snapshot, not a promise — re-verify against code for anything load-bearing.

**Working / done:**

- Config bugs fixed: `WALLET_PRIVATE_KEY`/`WALLET_ADDRESS`/`DRY_RUN` exist on `Config`; Sepolia Uniswap V2 Router02 address and full ABI populated; `WETH_ADDRESS` is a required config field (no more hardcoded mainnet WETH).
- `EthereumExecutor` (`apps/worker/core/trading/ethereum.py`) BUY and SELL both confirmed working via real signed Sepolia transactions (not just dry-run). SELL sells the actual wallet balance via `balanceOf`, not a hardcoded amount.
- `DRY_RUN` flag exists and gates signing/broadcast in `_execute_buy`, `_execute_sell`, `_approve_token_spending` — defaults to `True`.
- Infra (db/redis/adminer/api via `docker compose -f docker/run-development-compose.yaml`) brings up cleanly; Alembic migrations apply.
- `apps/worker/core/preflight.py` validates wallet/RPC/router config before a live run.
- `MarketDataProvider` interface added (mirrors the `llm/adapters/` pattern): `DexScreenerProvider` and `GeckoTerminalProvider` behind `config.MARKET_DATA_PROVIDER_CLASS`, defaulting to GeckoTerminal because **DexScreener does not index Sepolia testnet pools** (confirmed via direct API checks — this is a hard platform limitation, not a bug to "fix").
- Analyzer → executor wiring: `tasks/analyzer.py`'s `perform_llm_analysis` calls `EthereumExecutor.execute()` directly on a BUY/SELL decision (HOLD is a no-op). The old `mock_decision` bypass and hardcoded network default have been removed — network is now a required, explicitly-passed parameter. Still re-read the file before relying on this, it has been reworked multiple times (see git log).
- The default LLM path is now `OpenAiAdapter` pointed at OpenCode Go (`LLM_BASE_URL=https://opencode.ai/zen/go/v1`, `LLM_MODEL_NAME=deepseek-v4-flash` in `.env.example`). It was previously `ReplicateAdapter` (`llm/adapters/replicate.py`) running `google/gemini-2.5-flash`, set via `LLM_ADAPTER_CLASS`/`LLM_MODEL_NAME` in `.env.example` (config field is `LLM_ADAPTER_CLASS`, not `ADAPTER_CLASS` — `LLM_PROVIDER` is descriptive-only and not read by `load_client_class()`). `ReplicateAdapter` remains available as a commented alternative in `.env.example`; its async prediction polling and `LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS` (default 120s) apply to that adapter only. Currently blocked: OpenCode Go rejects requests without an `x-opencode-session` header and the default model ID `deepseek-v4-flash` is no longer in its model list (issue #41). End-to-end validation with OpenCode Go is issue #24.

**Not working / explicitly out of scope for now:**

- Risk controls — position sizing, stop-loss, daily loss cap, slippage limit — **do not exist anywhere in the pipeline**. This includes swap slippage protection: BUY passes a minimum output of 0. Their absence is a known gap, not an oversight to silently work around; adding them is future planned work, not implicit scope of unrelated tasks.
- Full pipeline end-to-end test on Sepolia (analysis → decision → live execution) — in progress, treat as unproven until a real tx hash from Sepolia Etherscan is captured.
- Webapp is not wired to the API.
- No scheduler. `apps/worker/bot.py` is a stub (task body is `pass`, localhost broker) and the beat block in `main.py` is commented out. Nothing runs the pipeline unattended.
- `GET /analysis/perform_analysis` (`apps/api/routes/analysis.py`) sends `perform_llm_analysis` with only the token and `store_results`, but the task raises when `network` is missing. Expected to fail; not run.
- One run can execute several trades: the `EthereumExecutor` call sits inside the per-pool loop in `perform_llm_analysis`, so each matching pool with a BUY/SELL decision triggers its own trade.
- The LLM prompt (`llm/llm_analysis.py`) contains price and indicator data only: no wallet balance, position or last trade. The model's "sentiment" and "volatility" outputs are not backed by any input data.
- No stored signals, trades or worker runs. Results go to Redis only when `store_results=True`.
- `OpenAiAdapter` sets no temperature, max tokens or timeout.
- Solana / multi-chain support — deferred. Planned via a `base.py` chain-executor interface in `core/trading/` mirroring the LLM adapter pattern, so Ethereum-specific code doesn't get redone later. Do not add chain-specific branching outside `core/trading/`.

**Before starting any task touching `core/trading/`, `config/settings.py`, or `tasks/analyzer.py`: re-read those files first.** They have changed shape several times; don't rely on descriptions above beyond "roughly what to expect."

## 3. Architecture Invariants

- **API** (`apps/api`): models in `apps/api/models/`, DB access only through `apps/api/repositories/` (never raw queries in routes), routes under `/api/v1`. Any SQLAlchemy model change requires a new Alembic migration — never hand-write raw SQL migrations, never edit/delete an already-applied migration file.
- **Worker** (`apps/worker`): Celery app in `main.py`/`bot.py`, tasks in `tasks/`. LLM providers live behind `llm/adapters/` selected via `LLM_ADAPTER_CLASS` (current default: `OpenAiAdapter`, pointed at OpenCode Go) — new LLM backends must follow this pattern, not add ad-hoc client code. Market data providers likewise live behind `core/market_data_providers/` selected via `MARKET_DATA_PROVIDER_CLASS`. Chain execution lives only in `core/trading/`.
- **Config**: one `pydantic-settings` `Config` class per service (`apps/worker/config/settings.py`, `apps/api` equivalent). Never read `os.environ` directly outside that class. New env-driven values go in `Config` — never a scattered `os.getenv()` call — and must be added to `env_vars/.env.example` and the relevant `docker/services/*.yaml` in the same change.
- **LLM authority**: LLM output is advisory. It may propose BUY/SELL/HOLD or flag risk, but trade size, limits and execution are enforced in code. The LLM must never set trade size or touch keys, text fetched from outside (news, token descriptions) is untrusted input, and numeric arithmetic belongs in code, not in the prompt.
- **Webapp**: React 19 + Vite + TS, minimal scaffold today — no router/state-manager assumptions without checking `apps/webapp/package.json` first.

## 4. Safety Rules (non-negotiable)

- **Never enable live/mainnet trading without explicit user instruction.** Default to Sepolia + `DRY_RUN=true`.
- **Never run mainnet swaps while the minimum output is 0.** Slippage protection is a hard prerequisite for any mainnet use (see MVP and roadmap).
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
| --- | --- |
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
- `OpenAiAdapter` only calls `/chat/completions`. OpenCode Go models served only through `/responses` (e.g. `gpt-5.6-luna`) or `/messages` (e.g. `qwen3.6-plus`) will not work with it without adapter changes. Models that exist only on OpenCode Zen return model-not-found on Go. OpenCode's endpoints have changed over time — confirm the base URL and available models with `GET <LLM_BASE_URL>/models` and a real key before relying on them.

## 8. Fixed Bugs (resolved issues)

### Issue #31: Historical and real-time data sources analyzed unrelated tokens

**Problem:** `perform_llm_analysis` in `apps/worker/tasks/analyzer.py` fetched historical data from CoinGecko (mainnet prices for a symbol like "USDC") and real-time data from GeckoTerminal (testnet pool prices for whatever pool matched the symbol), then combined them as if they described the same asset. This led to analyzing mismatched data (e.g., $0.9998 mainnet USDC vs. $0.111551 Sepolia USDC-test) without detection.

**Direction taken:** Keep CoinGecko historical data, but verify the GeckoTerminal-resolved pool's token address matches a known-address allowlist per network before combining series. Hard-fail (skip pair, log warning) on mismatch rather than silently combining data.

**Implementation:**

- Added `KNOWN_TOKEN_ADDRESSES` constant in `apps/worker/tasks/analyzer.py` (module-level, per-network per-token allowlist).
- Populated with verified Sepolia addresses (USDC: `0xbe72e441bf55620febc26715db68d3494213d8cb`, WETH: `0xfff9976782d46cc05630d1f6ebab18b2324d6b14`) and mainnet addresses (USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`, WETH: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`).
- Added verification step in `perform_llm_analysis` after `_resolve_token_address`: if token_id is in allowlist for the network and resolved address doesn't match, skip pair and log warning.
- Allowlist is opt-in: tokens not in the allowlist proceed without blocking (prevents regression for newly-supported tokens).
- Added tests in `apps/worker/tests/analyzer_tests.py` (TestAnalyzerAddressVerification class) covering: match proceeds, mismatch skips with warning, unknown token proceeds.

**Files changed:** `apps/worker/tasks/analyzer.py`, `apps/worker/tests/analyzer_tests.py`

### Issue #34: Correct token identity doesn't guarantee comparable prices

**Problem:** Issue #31's fix verified that the GeckoTerminal-resolved on-chain token address matched a known-good address before combining with CoinGecko historical data. However, this only verified *token identity* (same contract address), not *price comparability*. For USDC on Sepolia testnet, the resolved pool's `base_token_address` (`0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238`) is genuinely Circle's official Sepolia USDC contract, so the #31 check passes. Yet the two data series remain incomparable: historical data is real mainnet USDC (~$0.9998–$1.0000), while real-time data is a thin Sepolia testnet pool quoting ~$0.10–$0.11. Testnet tokens have no real economic backing, so their DEX prices reflect arbitrary pool seeding ratios, not real market value.

**Direction taken:** Add a price-plausibility sanity check that compares the real-time price against the historical trend for stablecoins only. Non-stablecoins like WETH are exempt since their prices can legitimately move. If deviation exceeds a threshold, skip the pair and log a warning (hard-fail, not silent combine).

**Implementation:**

- Added `STABLECOINS` constant in `apps/worker/tasks/analyzer.py` (module-level set: `{'USDC', 'USDT'}`) to scope the check to tokens with an expected ~$1 peg.
- Added `_is_price_plausible(historical_data, real_time_price, token_id)` function that:
  - Returns `(True, None, None)` for non-stablecoins (exempt).
  - Returns `(True, None, None)` if historical data is empty or invalid.
  - Computes percentage deviation between real-time price and most recent historical price.
  - Uses a 50% threshold: deviation > 50% is considered implausible.
  - Returns `(is_plausible, deviation, reference_price)` tuple.
- Wired the check into `perform_llm_analysis` after the existing address-verification step (issue #31) and before `combine_data`/`analyze_with_llm`.
- On failure: skip pair (`continue`) and log warning with token_id, network, historical reference price, real-time price, and computed deviation.
- Added tests in `apps/worker/tests/analyzer_tests.py` (TestAnalyzerPricePlausibility class) covering:
  - Stablecoin within threshold proceeds normally.
  - Stablecoin exceeding threshold (reproduces live ~89% deviation scenario) skips with warning.
  - Non-stablecoin (WETH) exempt even with large deviation.
  - Empty/invalid historical data skips check gracefully.
  - Integration tests calling real `perform_llm_analysis` for both plausible and implausible scenarios.

**Threshold and scoping rationale:**

- 50% threshold is a heuristic starting point, not a precisely-derived value. It's wide enough to avoid false positives on legitimate small deviations but narrow enough to catch the ~90% deviation observed in issue #34.
- Check scoped to stablecoins only because they have an expected ~$1 peg, making large deviations inherently suspicious. WETH and other volatile tokens are exempt since their prices can legitimately move for reasons that aren't necessarily "bad data" (different liquidity, no real arbitrage pressure on testnet).

**Files changed:** `apps/worker/tasks/analyzer.py`, `apps/worker/tests/analyzer_tests.py`

### Issue #33: Symbol-based token resolution unreachable for real GeckoTerminal data

**Problem:** `_resolve_token_address(token_id, pair)` in `apps/worker/tasks/analyzer.py` was meant to resolve an on-chain ERC20 address for a symbol like `"USDC"` from provider pair/pool data. For the GeckoTerminal-shaped branch (`elif 'base_token_address' in pair and 'quote_token_address' in pair:`), every comparison it performed was either address-vs-`token_id` or symbol-vs-`token_id`:

- Address comparisons (`base_address == token_id_lower`, etc.) could never succeed when `token_id` is a plain symbol like `"USDC"` rather than an address.
- Symbol comparisons (`pair.get('base_token_symbol', '')`, `pair.get('quote_token_symbol', '')`) could never succeed either, because `GeckoTerminalProvider.search_token_pairs` never sets those keys at all — it only ever adds `base_token_address`/`quote_token_address`, extracted from `relationships`, onto each pool dict. The keys `base_token_symbol`/`quote_token_symbol` are never present.
- The `relationships`-based fallback also only extracted an *address* from `relationships.base_token.data.id` (format `"{network}_{address}"`) and compared that address string against `token_id_lower` — same problem, it's still an address-vs-symbol comparison that can never match.

Net effect: for any symbol-based `token_id` (which is how this function is always actually called — see `perform_llm_analysis`, `trigger_full_pipeline.py`, `scripts/trigger_full_pipeline.py`), resolution against real GeckoTerminal data **always returned `None`**, and the calling loop's `if not token_address: continue` silently dropped every pair with no warning logged. This was confirmed live: a real pipeline run's HTTP request log showed only 2 requests (`coins/market_chart`, `search/pools`) and no third request to GeckoTerminal's `networks/{network}/pools/{pair_address}` endpoint — proof `get_realtime_data` was never reached for any pair.

**Why this matters beyond just "empty results":** this bug sat *before* both the issue #31 `KNOWN_TOKEN_ADDRESSES` check and the issue #34 price-plausibility check in the loop. Neither of those fixes' logic could ever execute for a symbol-based call while this bug existed, meaning neither had actually been live-verified yet despite passing their own unit tests and audits — the pipeline was already returning empty results for an unrelated, earlier reason.

**Direction taken:** Use `KNOWN_TOKEN_ADDRESSES` (added for #31) as a resolution mechanism, not just a verification one. If `token_id` (uppercased) is a known symbol for the current network in that allowlist, look up its expected address and check whether it equals the pair's `base_token_address` or `quote_token_address` (case-insensitive). If it matches either, that's the resolved address — return it. This reuses ground truth that's already audited and trusted, rather than introducing a new, separate resolution mechanism.

**Implementation:**

- Added `network` parameter to `_resolve_token_address(token_id, pair, network=None)` to enable allowlist-based resolution.
- Added allowlist-based resolution logic in the GeckoTerminal branch: when `token_id` is a plain symbol (not an address) and `network` is provided, normalize the network name via `_map_chain_to_executor_network`, look up the symbol in `KNOWN_TOKEN_ADDRESSES[normalized_network]`, and check if the pair's base or quote address matches the allowlisted address.
- Added debug-level logging for symbols not in the allowlist to provide visibility without spamming warnings for legitimately-unresolvable pairs.
- Updated the call to `_resolve_token_address` in `perform_llm_analysis` to pass the `network` parameter.
- Added tests in `apps/worker/tests/analyzer_tests.py` (TestAnalyzerSymbolResolutionViaAllowlist class) covering:
  - USDC symbol resolves via allowlist for Sepolia and mainnet.
  - WETH symbol resolves via allowlist for Sepolia.
  - Symbol not in allowlist returns None (existing behavior preserved).
  - Symbol resolution without network parameter returns None.
  - Address-based resolution still works when network parameter is provided.
- Added end-to-end integration tests (TestAnalyzerSymbolResolutionIntegration class) confirming that with this fix, a realistic GeckoTerminal-shaped pair **does** reach `get_realtime_data`, the #31 address verification check, and the #34 price-plausibility check, rather than being dropped at the first `if not token_address: continue`.

**Limitation:** This only helps for tokens already in `KNOWN_TOKEN_ADDRESSES` (currently `USDC`, `WETH` per network). Symbols outside that allowlist still can't be resolved this way, which is an acceptable limitation to state explicitly, not silently paper over.

**Note on reachability of prior fixes:** This fix is what makes issues #31 and #34 actually reachable/verifiable in a live run. Before this fix, neither prior audit could confirm that their logic would ever execute on a symbol-based call, since the pipeline was already returning empty results for an unrelated, earlier reason (symbol resolution failure).

**Files changed:** `apps/worker/tasks/analyzer.py`, `apps/worker/tests/analyzer_tests.py`

## 9. Where to Look Before Asking / Assuming

- Repo-local Devin knowledge base (`.devin/` — gitignored, local to Hendro's environment, not visible in a fresh clone): `rules/always-on/`, `rules/worker/known-bugs.md`, `architecture/overview.md`. Treat this file (`docs/SOURCE_OF_TRUTH.md`) as the version that travels with the repo itself.
- Implementation prompts and audit trail: `~/Documents/Work Projects/Cryptobot/Prompts` (outside this repo by design).
- Tracking board: `https://github.com/users/w33ladalah/projects/1`.
- `README.md` in repo root for setup/run instructions.

## Maintenance

This document should be updated whenever: a confirmed bug is fixed, a major architectural decision is made (e.g. a new provider interface), or the current phase/focus changes. Keep it accurate rather than comprehensive — stale specifics are worse than a pointer to "go read the code."
