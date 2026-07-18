---
name: scaffold-backend-entity
description: Scaffold a complete API entity (model, schema, repository, route) given an entity name and fields
---

# Scaffold API Entity

Given an **entity name** and a list of **fields**, create the full `apps/api` stack, following
the existing pattern in `apps/api/models/`, `apps/api/schema/`, `apps/api/repositories/`, and
`apps/api/routes/` (see e.g. `wallet.py` / `wallet_repository.py` for a reference example).

## What to generate

### 1. Model — `apps/api/models/<entity_snake>.py`

- Follow the column/mapping style already used in `apps/api/models/` (check an existing model
  like `token.py` before inventing a new base class pattern).
- Add the import in `apps/api/models/__init__.py`.

### 2. Schema — `apps/api/schema/<entity_snake>.py`

- `<Entity>Create` — fields required for creation.
- `<Entity>Update` — all fields optional.
- `<Entity>Response` — all fields + id/timestamps, with `model_config = {"from_attributes": True}`.

### 3. Repository — `apps/api/repositories/<entity_snake>_repository.py`

- Class `<Entity>Repository` with `__init__(self, db: Session)`.
- Methods: `get`, `get_all`, `create`, `update`, `delete`.
- Add tests under `apps/api/repositories/tests/`.

### 4. Route — `apps/api/routes/<entity_snake>.py`

- `router = APIRouter()`.
- Standard endpoints: `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`.
- Register in `apps/api/routes/__init__.py` so it's mounted under `/api/v1`.

### 5. Remind user to run migration

Print: "Run `/database-migration` to create the Alembic migration for this new model."
