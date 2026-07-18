---
trigger: model_decision
description: Environment variable and secrets management rules
---

# Secrets & Environment Management

## Environment File Locations

| File | Purpose |
|------|---------|
| `.env` (root) | Shared secrets: AWS, Replicate, Postgres, Redis |
| `backend/.env` | Backend-specific config |
| `frontend/.env` | `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_GOOGLE_CLIENT_ID` |
| `admin/.env` | `NEXT_PUBLIC_API_URL` |

## Rules

- **Never commit `.env` files** — all are gitignored
- **Never hardcode secrets** in source code (API keys, passwords, tokens)
- **Never log secrets** even at DEBUG level
- Use `.env.example` as template — copy to `.env` for new setups
- Access config only via `from app.core.config import settings` (backend)

## Public vs Private ENV Vars (Frontend/Admin)

- `NEXT_PUBLIC_*` prefix = exposed to browser — safe only for non-secret values
- Never put secrets in `NEXT_PUBLIC_*` variables

## Backend Config Pattern

```python
from app.core.config import settings

# Access any config value
settings.AWS_S3_BUCKET_NAME
settings.REPLICATE_API_TOKEN
settings.DATABASE_URL
```

All values loaded from environment via pydantic-settings in `app/core/config.py`.
DB-backed overrides via `apply_db_overrides()` — sensitive keys in `DB_OVERRIDE_DENYLIST` are never overridden.
