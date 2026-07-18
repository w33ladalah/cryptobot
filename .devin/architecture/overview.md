---
trigger: model_decision
description: High-level system architecture overview for Crypto Bot
---

# Crypto Bot — System Architecture Overview

## Platform Summary

Crypto Bot analyzes crypto market data (CoinGecko + DexScreener) using an LLM to produce
BUY/SELL/HOLD decisions, and (eventually) executes trades on Ethereum via Uniswap. It is an
experimental, in-progress project — not fully working yet. Current focus: Ethereum on Sepolia
testnet, DRY_RUN-first.

## Architecture Layers

```
┌───────────────────────────────────────────────────┐
│  Webapp (React 19 + Vite + TS)                     │
│  localhost:1421 — dashboard, not yet wired to API   │
└──────────────────────┬──────────────────────────────┘
                        │ (planned: Axios/fetch)
                        ▼
┌───────────────────────────────────────────────────┐
│  FastAPI API (apps/api, Python)                     │
│  /api/v1 — platforms, users, wallets, analysis      │
└──────────────────────┬──────────────────────────────┘
                        │
┌──────▼──────┐  ┌──────▼────────────────────────────┐
│ MySQL       │  │ Redis (Celery broker + result       │
│ (Alembic)   │  │ backend, shared by api + worker)    │
└─────────────┘  └──────────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────┐
│  Celery Worker (apps/worker, Python)                │
│  ┌────────────────┐  ┌─────────────────────────┐   │
│  │ Market data     │  │ LLM analysis            │   │
│  │ (core/market_   │  │ (llm/llm_analysis.py +  │   │
│  │  data.py)       │  │  llm/adapters/*)        │   │
│  └────────────────┘  └─────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐  │
│  │ Trade execution (core/trading/ethereum.py)     │  │
│  │ — currently broken, see rules/worker/          │  │
│  │   known-bugs.md — not wired to analysis yet    │  │
│  └──────────────────────────────────────────────┘  │
└───────────────────────┬───────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────┐
│  External Services                                  │
│  ├── CoinGecko API, DexScreener API (market data)   │
│  ├── OpenRouter / Ollama (LLM backends, via adapters)│
│  ├── Discord (bot notifications)                    │
│  ├── Infura (Ethereum RPC — mainnet + testnet)       │
│  └── Uniswap Router (on-chain swaps)                 │
└───────────────────────────────────────────────────┘
```

## Key Data Flows

### Analysis Flow (implemented)
```
Celery beat schedule → tasks/data_sources.py fetches CoinGecko/DexScreener data
  → tasks/analyzer.py's perform_llm_analysis() → LLM adapter (llm/adapters/) → decision
  → analysis result stored via apps/api repositories
```

### Execution Flow (NOT yet implemented end-to-end)
```
LLM decision (BUY/SELL/HOLD) → [MISSING WIRING] → EthereumExecutor (core/trading/ethereum.py)
  → Uniswap swap on configured chain → tx result
```
As of 2026-07-17 this path is broken/unwired — see `rules/worker/known-bugs.md` for the specific
bugs (config attrs that don't exist, signature mismatch, mainnet-hardcoded router, deprecated
Kovan testnet URL) and `rules/always-on/core-principles.md` for the current fix plan.

## Domain Models (`apps/api/models`)

| Domain | Key Models |
|--------|-----------|
| Platform | Platform (`platform.py`) |
| Users | User (`users.py`) |
| Wallet | Wallet (`wallet.py`) |
| Tokens | Token, TokenPair (`token.py`, `token_pair.py`) |
| Analysis | Analysis (`analysis.py`) — LLM decisions + market snapshots |

## Multi-Chain Design (planned, not built)

The LLM adapter pattern (`apps/worker/llm/adapters/`, selected via `ADAPTER_CLASS` config) is the
template for a future chain-executor abstraction: a `base.py` interface in `core/trading/` with
`ethereum.py` as the first concrete implementation, so Solana or other chains can be added later
without touching Ethereum-specific code.

## See Also

- `rules/worker/known-bugs.md` — confirmed bugs blocking the Ethereum execution path
- `rules/always-on/core-principles.md` — current focus and 7-step plan to Sepolia end-to-end
