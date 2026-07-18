---
trigger: glob
globs: apps/api/**
description: Alembic migration rules — always generate and apply after any model change
---

# Database Migrations

## When Required

After ANY change to SQLAlchemy models in `apps/api/models/`:
- Adding/removing columns
- Changing column types or constraints
- Adding/removing indexes
- New tables
- Renaming columns

## Steps

```bash
# 1. Generate migration (inside the api container)
docker compose -f docker/run-development-compose.yaml exec api alembic revision --autogenerate -m "describe change"

# 2. Review the generated file in apps/api/alembic/versions/
# Verify upgrade() and downgrade() are correct

# 3. Apply
docker compose -f docker/run-development-compose.yaml exec api alembic upgrade head

# 4. Verify
docker compose -f docker/run-development-compose.yaml exec api alembic current
```

## Rules

- **Never** run Alembic directly on host — always inside the `api` container.
- **Never delete or modify** migration files that have already been applied.
- If a migration fails: `alembic downgrade -1` inside the container, then fix and regenerate.
- Always provide a descriptive migration message (not just "update" or "fix").
- The `db` and `api` containers must be running before running migrations.

## New Model Checklist

1. Model added to `apps/api/models/<entity>.py`
2. Model exported from `apps/api/models/__init__.py`
3. Migration generated and reviewed
4. Migration applied and verified with `alembic current`
