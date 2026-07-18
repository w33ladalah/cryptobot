---
name: add-celery-task
description: Add a new Celery background task to the backend
---

# Add Celery Task

Given a **task name** and **description of what it does**, create a Celery task:

## What to generate

### 1. Task file — `backend/app/tasks/<task_name>.py`

```python
from app.core.celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

def _get_async_session_factory():
    engine = create_async_engine(
        settings.database_url, echo=False, future=True, poolclass=NullPool
    )
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False), engine

@celery_app.task(name="<task_name>_task", bind=True, max_retries=3)
def <task_name>_task(self, **kwargs):
    """<task description>"""
    factory, engine = _get_async_session_factory()

    async def _run():
        try:
            async with factory() as db:
                # Task logic here
                pass
        finally:
            await engine.dispose()

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.error(f"Task <task_name> failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
```

### 2. Register in Celery app

Add the task module to the `include` list in `backend/app/core/celery_app.py`:

```python
include=[
    ...,
    "app.tasks.<task_name>",
]
```

### 3. Add Beat schedule (if periodic)

If the task should run on a schedule, add to `celery_app.conf.beat_schedule` in `celery_app.py`.

## Key patterns

- Celery tasks are **synchronous** — use `asyncio.run()` to call async code.
- Create a **fresh engine per task** with `NullPool` (tasks run in worker processes, not the main app).
- Always `await engine.dispose()` in a `finally` block.
- Use `bind=True` + `self.retry()` for automatic retries.
- Task name string must be unique across all tasks.
