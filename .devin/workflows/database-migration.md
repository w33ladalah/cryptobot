---
description: How to create a database migration with Alembic
---

# Database Migration Workflow

## Steps

1. **Create the SQLAlchemy model** (or modify an existing one) in `apps/api/models/`.

2. **Register the model** in `apps/api/models/__init__.py` if it's a new model — the import
   makes Alembic aware of it for autogeneration.

3. **Generate the migration** inside the `api` container:

```bash
docker compose -f docker/run-development-compose.yaml exec api alembic revision --autogenerate -m "describe your change"
```

4. **Review the generated migration** in `apps/api/alembic/versions/`.
   - Verify `upgrade()` and `downgrade()` are correct.
   - Check for missing indexes, constraints, or defaults.

5. **Apply the migration:**

```bash
docker compose -f docker/run-development-compose.yaml exec api alembic upgrade head
```

6. **Verify:**

```bash
docker compose -f docker/run-development-compose.yaml exec api alembic current
```

## Important Notes

- **Never run Alembic directly on the host** — always inside the `api` container.
- **Never delete or modify existing migration files** that have already been applied.
- If a migration fails: `alembic downgrade -1` to revert.
- The `api` and `db` containers must be running first.
