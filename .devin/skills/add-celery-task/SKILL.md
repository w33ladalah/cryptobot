---
name: add-celery-task
description: Add a new Celery background task to apps/worker
---

# Add Celery Task

Given a **task name** and **description of what it does**, create a Celery task following the
existing pattern in `apps/worker/bot.py` / `apps/worker/tasks/`.

## What to generate

### 1. Task file — `apps/worker/tasks/<task_name>.py`

```python
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def <task_name>_task(self, **kwargs):
    """<task description>"""
    try:
        # Task logic here — use apps/worker/config/settings.py's Config for any settings,
        # apps/worker/core/ for market data / trading / sentiment logic
        pass
    except Exception as exc:
        logger.error(f"Task <task_name> failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
```

Match the style already used in `apps/worker/tasks/analyzer.py` and `data_sources.py` — check
those first rather than assuming a framework not present in this codebase (there is no async
SQLAlchemy session factory pattern here; the worker mostly calls `apps/api` over HTTP or talks
to Redis/CoinGecko/DexScreener/LLM/web3 directly).

### 2. Register the task

Celery in this project is set up in `apps/worker/main.py` / `bot.py` — ensure the task module is
imported so Celery discovers it (check how `tasks/analyzer.py` and `tasks/data_sources.py` are
currently wired in before assuming an `include=[...]` list exists).

### 3. Add to beat schedule (if periodic)

`apps/worker/bot.py` currently defines `beat_schedule` inline (e.g. `run-every-5-minutes`) — add
a new entry there if the task should run on a schedule.

## Key patterns

- Task name string must be unique across all tasks.
- Use `bind=True` + `self.retry()` for automatic retries on transient failures.
- If the task touches `apps/worker/core/trading/`, check `rules/worker/known-bugs.md` first.
- Trade-execution tasks must default to DRY_RUN/Sepolia — see `rules/always-on/safety.md`.
