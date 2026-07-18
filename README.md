# Crypto Bot

**PLEASE REMEMBER THIS PROJECT IS STILL ON PROGRESS AND EXPERIMENTAL! IT IS NOT FULLY WORKING YET!**

A bot to analyze market and do auto-buying according to analysis result.

## Current Status (2026-07-18)

This project was paused for a long stretch and, per the warning above, still isn't fully working end-to-end. Current focus is getting the **Ethereum trading path running against Sepolia testnet** before anything else (Solana support and mainnet trading are deliberately deferred later phases).

Done so far:

- Fixed worker config bugs that made `EthereumExecutor` unrunnable (missing `WALLET_PRIVATE_KEY`/`ERC20_ABI` config fields, a mismatched `_execute_buy` signature, a hardcoded mainnet Uniswap router address, and a deprecated Kovan testnet RPC URL — see `apps/worker/config/settings.py` and `apps/worker/core/trading/ethereum.py`).
- Added `apps/worker/core/preflight.py` — a config validator you can run before touching a live Sepolia connection (see [Preflight Check](#preflight-check) below).

Still pending:

- Bringing up the full local infra stack (db/redis/adminer) and running migrations.
- Testing `EthereumExecutor` in isolation against a live Sepolia connection.
- Wiring the LLM's BUY/SELL/HOLD decision through to actual trade execution (currently analysis and execution aren't connected).
- Risk controls (position sizing, stop-loss, daily loss cap, slippage limit) — none exist yet.

## Overview

Crypto Bot is an automated trading bot designed to analyze market data and execute trades based on predefined strategies. It utilizes LLM to detect trends using data from CoinGecko and DexScreener.

## Features

- **Market Analysis**: Fetches and analyzes market data from sources like CoinGecko and DexScreener.
- **Automated Trading**: Executes buy and sell orders on Ethereum using Uniswap.
- **Data Storage**: Stores analysis results and historical data in a database.
- **Web Interface**: Provides a web interface for monitoring and managing the bot.

## Project Structure

```plaintext
crypto-bot/
├── apps/
│   ├── api/
│   │   ├── alembic/
│   │   ├── config/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── schema/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── webapp/
│   │   ├── src/
│   │   ├── public/
│   │   ├── index.html
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── worker/
│   │   ├── core/
│   │   ├── tasks/
│   │   ├── __init__.py
│   │   └── requirements.txt
├── docker/
│   ├── environments/
│   ├── services/
│   ├── docker-compose.yaml
├── scripts/
│   ├── generate_compose_file.sh
│   ├── manage_services.sh
├── env_vars/
│   ├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Docker
- Docker Compose
- Python 3.8+
- Node.js 14+

### Setup

1. Clone the repository:

    ```sh
    git clone https://github.com/w33ladalah/crypto-bot.git
    cd crypto-bot
    ```

2. Copy the example environment variables file and configure it:

    ```sh
    cp env_vars/.env.example env_vars/.env
    ```

3. Build and start the Docker containers:

    ```sh
    ./scripts/generate_compose_file.sh
    ./scripts/manage_services.sh
    ```

## Usage

### API

The API is built with FastAPI and provides endpoints for managing platforms, users, wallets, and analysis results.

- **Base URL**: `/api/v1`
- **Documentation**: `/docs`

### Web Interface

The web interface is built with React and Vite. It provides a dashboard for monitoring the bot's activities.

- **URL**: `http://localhost:1421`

### Worker

The worker is responsible for fetching market data, performing analysis, and executing trades. It uses Celery for task management.

#### Preflight Check

Before running the worker against Sepolia, validate your environment is set up correctly:

```sh
cd apps/worker
python -m core.preflight
```

This checks that `WALLET_PRIVATE_KEY` and `WALLET_ADDRESS` are present and well-formed, that `INFURA_URL_TESTNET` points at Sepolia (not a leftover placeholder or a mainnet URL), and that `UNISWAP_ROUTER_ADDRESS` is a valid Sepolia router address rather than the mainnet one. It prints every problem found and exits non-zero if anything's wrong — it does not itself generate a wallet, fund it, or set up an RPC provider account; those are manual steps (see Configuration below).

## Configuration

Configuration settings are managed through environment variables. Copy `env_vars/.env.example` to `env_vars/.env` and fill it in — see that file's inline comments for details on each section. A few of the trickier ones for Ethereum/Sepolia work specifically:

- `WALLET_PRIVATE_KEY` / `WALLET_ADDRESS` — a dedicated **test** wallet, never a wallet holding real funds. Generate one via MetaMask ("Create account") or `cast wallet new` (Foundry), then fund it with Sepolia ETH from a faucet (e.g. the Google Cloud Web3 faucet or Alchemy's Sepolia faucet).
- `INFURA_URL_TESTNET` — sign up for a free project at [infura.io](https://app.infura.io) (or Alchemy's equivalent) and drop your project's Sepolia endpoint in here. This is the only Infura URL the worker currently reads (`INFURA_URL_MAINNET` is unused until mainnet trading is in scope).
- `UNISWAP_ROUTER_ADDRESS` — must be the **Sepolia** Uniswap V2 Router02 address (`0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3`, per [Uniswap's official deployments page](https://developers.uniswap.org/docs/protocols/v2/deployments)), not the mainnet one. Run the preflight check above to catch this kind of mix-up automatically.
- `DRY_RUN` — when set to `true` (default), the EthereumExecutor logs intended BUY/SELL/approval transactions instead of signing and broadcasting them. Set to `false` only when ready to trade with real funds.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries, please contact Hendro Wibowo at [hendrothemail@gmail.com](mailto:hendrothemail@gmail.com).
