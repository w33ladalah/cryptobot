---
description: How to add a new API endpoint to the backend
---

# Add API Endpoint Workflow

## Steps

### 1. Define the Pydantic schemas

Create or update schemas in `backend/app/schemas/`:

```python
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class EntityCreate(BaseModel):
    name: str
    description: Optional[str] = None

class EntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class EntityResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
```

### 2. Create the CRUD class

Create `backend/app/crud/<entity>.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.<entity> import Entity

class EntityCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, entity_id):
        result = await self.db.execute(select(Entity).filter(Entity.id == entity_id))
        return result.scalars().first()

    async def create(self, data):
        entity = Entity(**data.model_dump())
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
```

### 3. Create the router

Create `backend/app/routers/<entity>.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter()
public_router = APIRouter()  # Only if public endpoints are needed
```

### 4. Register the router

- **Protected routes:** Add to `backend/app/api/__init__.py`:

  ```python
  from app.routers import <entity>
  api_router.include_router(<entity>.router, prefix="/<entities>", tags=["<entities>"])
  ```

- **Public routes:** Add directly in `backend/main.py`:

  ```python
  from app.routers.<entity> import public_router as <entity>_public_router
  app.include_router(<entity>_public_router, prefix="/api/<entities>", tags=["<entities>"])
  ```

- **Admin routes:** Add to `backend/app/api/__init__.py` with `admin` prefix:

  ```python
  from app.routers import admin_<entity>
  api_router.include_router(admin_<entity>.router, prefix="/admin/<entities>", tags=["admin-<entities>"])
  ```

### 5. Test the endpoint

After the backend auto-reloads (uvicorn `--reload`), test via:

- Swagger UI: `http://localhost:8000/docs`
- Or `curl` / Postman / the frontend

### 6. Update the frontend API endpoints

Add the new endpoint to `frontend/src/constants/apiEndpoints.ts`:

```typescript
ENTITY: {
  LIST: `${API_BASE_URL}/api/<entities>`,
  GET: (id: string) => `${API_BASE_URL}/api/<entities>/${id}`,
  CREATE: `${API_BASE_URL}/api/<entities>`,
},
```
