---
trigger: glob
globs: backend/**
description: Alembic migration rules — always generate and apply after any model change
---

# Database Migrations

## When Required

After ANY change to SQLAlchemy models in `backend/app/models/`:
- Adding/removing columns
- Changing column types or constraints
- Adding/removing indexes
- New tables
- Renaming columns

## Steps

```bash
# 1. Generate migration
docker compose exec backend alembic revision --autogenerate -m "describe change"

# 2. Review generated file in backend/migrations/versions/
# Verify upgrade() and downgrade() are correct

# 3. Apply
docker compose exec backend alembic upgrade head

# 4. Verify
docker compose exec backend alembic current
```

## Rules

- **Never** run Alembic directly on host — always inside Docker
- **Never delete or modify** migration files that have been applied in production
- If migration fails: `docker compose exec backend alembic downgrade -1`
- Always provide a descriptive migration message (not just "update" or "fix")
- The backend container must be running before running migrations

## New Model Checklist

1. Model extends `BaseModel` from `app/models/base.py`
2. Model registered in `backend/app/models/__init__.py`
3. Migration generated and applied
4. Migration reviewed before applying
