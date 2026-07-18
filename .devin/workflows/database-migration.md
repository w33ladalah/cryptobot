---
description: How to create a database migration with Alembic
---

# Database Migration Workflow

## Steps

1. **Create the SQLAlchemy model** (or modify an existing one) in `backend/app/models/`.
   - Extend `BaseModel` from `app/models/base.py` for auto `created_at`/`updated_at`.
   - Use `Mapped[]` + `mapped_column()` (SQLAlchemy 2.0 style).
   - UUIDs as primary keys: `mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`.

2. **Register the model** in `backend/app/models/__init__.py` if it's a new model.
   - Add the import so Alembic can detect it.

3. **Generate the migration** inside the Docker container:

// turbo
```bash
docker compose exec backend alembic revision --autogenerate -m "describe your change"
```

4. **Review the generated migration** in `backend/migrations/versions/`.
   - Verify the `upgrade()` and `downgrade()` functions are correct.
   - Check for any missing index, constraints, or default values.

5. **Apply the migration:**

// turbo
```bash
docker compose exec backend alembic upgrade head
```

6. **Verify** the migration applied correctly:

// turbo
```bash
docker compose exec backend alembic current
```

## Important Notes

- **Never run Alembic directly on the host** — always inside the Docker container.
- **Never delete or modify existing migration files** that have been applied in production.
- If a migration fails, use `docker compose exec backend alembic downgrade -1` to revert.
- The backend container must be running (`docker compose up -d backend db`).
