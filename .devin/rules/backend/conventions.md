---
trigger: glob
globs: backend/**
description: Backend conventions for FastAPI, SQLAlchemy 2.0, CRUD, routers, and schemas
---

# Backend Conventions

## Tech Stack

- FastAPI 0.100+ with uvicorn (`--reload` in dev)
- SQLAlchemy 2.0 async with asyncpg
- Alembic 1.16+ for migrations
- Celery 5.3+ with Redis broker
- pydantic-settings for config (`app/core/config.py` → `Settings`)

## Models

```python
from app.models.base import BaseModel  # provides created_at, updated_at
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

class MyEntity(BaseModel):
    __tablename__ = "my_entities"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
```

- Register in `backend/app/models/__init__.py`
- Relationships use `lazy="raise"` by default (explicit loading required)
- Use `values_callable=lambda x: [e.value for e in x]` for SQLEnum str enums

## CRUD

```python
class EntityCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, entity_id: UUID):
        result = await self.db.execute(select(Entity).filter(Entity.id == entity_id))
        return result.scalars().first()

def get_entity_crud(db: AsyncSession = Depends(get_db)) -> EntityCRUD:
    return EntityCRUD(db)
```

- One CRUD class per entity in `app/crud/`
- Use `select()` from `sqlalchemy.future`

## Schemas

```python
from pydantic import BaseModel

class EntityCreate(BaseModel):
    name: str

class EntityUpdate(BaseModel):
    name: str | None = None

class EntityResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    model_config = {"from_attributes": True}
```

## Routers

```python
router = APIRouter()           # protected — register in app/api/__init__.py
public_router = APIRouter()    # public — mount in main.py with explicit prefix
```

- Admin routes: prefix `/api/admin/`, dependency `get_current_active_admin`
- Protected routes: use `get_current_active_user` dependency

## Auth Dependencies

- `get_current_active_user` — regular authenticated user
- `get_current_active_admin` — admin user
- `get_current_active_talent` — talent user
- `get_current_active_superuser` — superuser

## Settings

```python
from app.core.config import settings  # singleton
```

DB-backed overrides via `apply_db_overrides()`. Sensitive keys in `DB_OVERRIDE_DENYLIST` are never overridden.

## Celery Tasks

- Task files in `app/tasks/`
- Registered in `app/core/celery_app.py` `include` list
- Beat schedule configured in `celery_app.py`

## Concurrency & External API Calls

### Rule 1 — Always use `run_in_threadpool` for Replicate SDK calls

The `replicate` Python SDK (`replicate_client.predictions.create/cancel/get`) is **synchronous**. Calling it directly inside an `async` function blocks the entire asyncio event loop, freezing all pending coroutines and preventing DB connections from being returned to the pool.

```python
# CORRECT
from fastapi.concurrency import run_in_threadpool

replicate_prediction = await run_in_threadpool(
    replicate_client.predictions.create,
    model=settings.MODEL,
    input=input_data,
)

# WRONG — blocks the event loop
replicate_prediction = replicate_client.predictions.create(
    model=settings.MODEL,
    input=input_data,
)
```

This rule applies to `.create()`, `.cancel()`, and `.get()` calls.

### Rule 2 — Commit DB before any external API call

In SQLAlchemy 2.0 autobegin, `await session.commit()` **immediately returns the connection to the pool**. Always commit any pending DB writes before making an external HTTP call (Replicate, S3, etc.) so the connection is free during the network wait.

```python
# CORRECT
prediction = await prediction_crud.create(...)
await db.commit()                          # ← connection released here

replicate_prediction = await run_in_threadpool(  # no connection held during this
    replicate_client.predictions.create, ...
)

# WRONG — connection held during the entire Replicate call
prediction = await prediction_crud.create(...)
replicate_prediction = await run_in_threadpool(
    replicate_client.predictions.create, ...
)
await db.commit()
```

## Timezone

- `now_gmt7()` — user-facing timestamps (display)
- `datetime.now(timezone.utc)` — database comparisons, JWT expiry, license checks

```python
from app.core.timezone import now_gmt7, GMT7
```
