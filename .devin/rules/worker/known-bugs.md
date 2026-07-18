---
trigger: glob
globs: apps/worker/**
description: Known bugs and gotchas in the worker that must not be reintroduced
---

# Worker Known Bugs & Gotchas

Confirmed by direct code read on 2026-07-17 — not assumptions. Do not treat any of these as
already fixed unless you've re-verified against current code.

## 1. Missing Config Attributes in `ethereum.py`

**File:** `apps/worker/core/trading/ethereum.py`

References `config.ETH_PRIVATE_KEY` and `config.ERC20_ABI`, neither of which exist on the
`Config` class (`apps/worker/config/settings.py`). The class only defines `WALLET_PRIVATE_KEY`
(and no `ERC20_ABI` at all). This makes the module fail at attribute-access time.

**Fix approach:** add the missing fields to `Config`, or point `ethereum.py` at the existing
`WALLET_PRIVATE_KEY`/`WALLET_ADDRESS` fields — don't invent a second parallel set of wallet
config names.

## 2. `_execute_buy()` Signature Mismatch

`_execute_buy()` is defined with 4 parameters but called with 3 args at its call site — the BUY
path is unrunnable as-is. Fix the call site or the signature based on which one reflects the
intended contract (check git history / any related tests before choosing).

## 3. Uniswap Router Hardcoded to Mainnet

`UNISWAP_ROUTER_ABI` defaults to `[]` (empty), and the router address is hardcoded to Uniswap
**mainnet**. This is unsafe to reuse for Sepolia — mainnet and Sepolia router contracts are
different addresses. Needs a Sepolia router address + real ABI before any testnet execution
attempt.

## 4. `INFURA_URL_TESTNET` Points at Deprecated Kovan

`env_vars/.env.example`'s `INFURA_URL_TESTNET` is documented/intended for Kovan, which has been
deprecated for years. Must point at Sepolia instead.

## 5. No `.env` File Exists Yet

Only `env_vars/.env.example` exists; `env_vars/.env` has never been created. `CELERY_BROKER_URL`
and `CELERY_RESULT_BACKEND` have no defaults in `Config`, so the worker will not boot without a
real `.env` in place.

## 6. Analysis → Execution Pipeline Is Not Wired

`tasks/analyzer.py`'s `perform_llm_analysis()` returns an LLM BUY/SELL/HOLD decision, but nothing
currently calls `EthereumExecutor` with that decision. There are also no risk controls anywhere
in the pipeline (position sizing, stop-loss, daily loss cap, slippage limit) — adding these is
planned work, not something already handled elsewhere.

## See Also

`rules/always-on/core-principles.md` for the current 7-step plan to get Ethereum working
end-to-end on Sepolia (fix config → add Sepolia router → set up `.env` + test wallet → bring up
infra → test executor in isolation → add DRY_RUN flag → run full pipeline on testnet).
