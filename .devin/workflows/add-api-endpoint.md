---
description: How to add a new API endpoint to apps/api
---

# Add API Endpoint Workflow

## Steps

### 1. Define the model (if new entity)

Add to `apps/api/models/<entity>.py`, export from `apps/api/models/__init__.py`, then generate
an Alembic migration (see `/database-migration`).

### 2. Create/extend the repository

`apps/api/repositories/<entity>_repository.py`:

```python
class EntityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, entity_id):
        return self.db.query(Entity).filter(Entity.id == entity_id).first()
```

Repository tests go in `apps/api/repositories/tests/`.

### 3. Define request/response schema

`apps/api/schema/<entity>.py`:

```python
from pydantic import BaseModel

class EntityCreate(BaseModel):
    name: str

class EntityResponse(BaseModel):
    id: str
    name: str
    model_config = {"from_attributes": True}
```

### 4. Create the route

`apps/api/routes/<entity>.py`:

```python
from fastapi import APIRouter, Depends

router = APIRouter()
```

### 5. Register the route

Add to `apps/api/routes/__init__.py` so it's mounted under `/api/v1`.

### 6. Test the endpoint

After the `api` container auto-reloads (`fastapi dev`), test via:

- Swagger UI: `http://localhost:<API_PORT>/docs`
- Or `curl` / Postman

No frontend wiring is expected by default — `apps/webapp` has no API client set up yet
(see `rules/frontend/conventions.md`); only add that if asked.
