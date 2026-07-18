---
trigger: glob
globs: apps/api/**,apps/worker/**
description: Conventions for the FastAPI API and the Celery worker
---

# API & Worker Conventions

## Tech Stack

- **API** (`apps/api`): FastAPI 0.115, SQLAlchemy 2.0, Alembic, Celery/Redis client, pydantic-settings.
- **Worker** (`apps/worker`): Celery 5.4 + Redis broker, web3.py 7.x, eth-account, langchain-core /
  openai / ollama for LLM calls.
- Both run as separate containers (`docker/services/api.yaml`, `docker/services/worker.yaml`);
  they share the same MySQL DB and Redis instance but are separate Python environments with
  separate `requirements.txt`.

## API — Models

```python
from sqlalchemy.orm import Mapped, mapped_column
# apps/api/models/<entity>.py — see existing models for the base class pattern
```

- Model files live in `apps/api/models/` (`analysis.py`, `platform.py`, `token.py`,
  `token_pair.py`, `users.py`, `wallet.py`) and must be exported from `apps/api/models/__init__.py`.
- Any model change requires a new Alembic migration (`apps/api/alembic/versions/`).

## API — Repositories

```python
class TokenRepository:
    def __init__(self, db: Session):
        self.db = db
```

- One repository per entity in `apps/api/repositories/` (e.g. `token_pair_repositories.py`,
  `wallet_repository.py`). Routes call repositories — they do not query the DB directly.
- Repository tests live in `apps/api/repositories/tests/`.

## API — Routes

- Route files live in `apps/api/routes/` (`analysis.py`, `data_source.py`, `platform.py`,
  `token.py`, `token_pair.py`, `user.py`) and are mounted under `/api/v1` from
  `apps/api/routes/__init__.py`.

## API — Config

```python
from apps.api.config import ...  # pydantic-settings, mirrors apps/worker/config/settings.py
```

Config values (DB creds, rate limit, DexScreener/CoinGecko URLs, encryption secret) come from
env vars via pydantic-settings — never hardcode or read `os.environ` directly in routes/repos.

## Worker — Tasks

- Task files live in `apps/worker/tasks/` (`analyzer.py`, `data_sources.py`), Celery app is set
  up in `apps/worker/main.py` / `bot.py`.
- Beat schedule is defined alongside the Celery app (see `bot.py`'s `beat_schedule`).
- Tasks that call the LLM go through `apps/worker/llm/llm_analysis.py`, which delegates to the
  adapter selected by the `ADAPTER_CLASS` config value (`apps/worker/llm/adapters/`) — don't call
  an LLM SDK directly from a task.

## Worker — Config

```python
from apps.worker.config.settings import Config
config = Config()
```

- Single `Config` class (`apps/worker/config/settings.py`), `pydantic-settings` + `SecretStr` for
  anything sensitive (`WALLET_PRIVATE_KEY`, `LLM_API_KEY`, `DISCORD_BOT_TOKEN`, etc).
- Add new env-driven values here rather than reading `os.getenv()` ad hoc — see current known gaps
  in `rules/worker/known-bugs.md` (e.g. `ETH_PRIVATE_KEY`/`ERC20_ABI` referenced but not defined).

## Worker — Trade Execution

- Chain execution logic lives in `apps/worker/core/trading/` — currently only `ethereum.py`
  (uses `web3.py`). Do not put Uniswap/web3 calls anywhere else.
- Check `rules/worker/known-bugs.md` before modifying this module — several confirmed bugs make
  it non-functional as of 2026-07-17.
