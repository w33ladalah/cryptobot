---
name: scaffold-backend-entity
description: Scaffold a complete backend entity (model, schema, CRUD, router) given an entity name and fields
---

# Scaffold Backend Entity

Given an **entity name** and a list of **fields**, create the full backend stack:

## What to generate

### 1. Model — `backend/app/models/<entity_snake>.py`

- Class inherits `BaseModel` from `app.models.base`.
- Table name: plural snake_case (e.g., `vouchers`).
- UUID primary key: `mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)`.
- Use `Mapped[]` + `mapped_column()` for all columns.
- Add the import in `backend/app/models/__init__.py`.

### 2. Schema — `backend/app/schemas/<entity_snake>.py`

- `<Entity>Create` — fields required for creation.
- `<Entity>Update` — all fields optional.
- `<Entity>Response` — all fields + `id`, `created_at`, `updated_at`, with `model_config = {"from_attributes": True}`.

### 3. CRUD — `backend/app/crud/<entity_snake>.py`

- Class `<Entity>CRUD` with `__init__(self, db: AsyncSession)`.
- Methods: `get`, `get_all` (with pagination), `create`, `update`, `delete`.
- Export a `get_<entity>_crud(db)` dependency function.

### 4. Router — `backend/app/routers/<entity_snake>.py`

- `router = APIRouter()` for protected endpoints.
- `public_router = APIRouter()` if any public endpoints are needed.
- Standard CRUD endpoints: `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`.
- Use `Depends(get_db)` for database sessions.

### 5. Register the router

- Add to `backend/app/api/__init__.py` for protected routes.
- Add to `backend/main.py` for public routes (if any).

### 6. Remind user to run migration

Print: "Run `/database-migration` to create the Alembic migration for this new model."
