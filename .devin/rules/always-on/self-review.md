---
trigger: always_on
description: Self-review checklist Cascade must apply before suggesting any commit or completion
---

# Self-Review Checklist

Before suggesting a git commit or declaring a task complete, verify:

## Code Quality

- [ ] Changes are minimal and focused (no accidental refactoring of unrelated code)
- [ ] Imports are at the top of every file (no mid-file imports unless circular import forces it)
- [ ] No new comments added or removed unless explicitly asked
- [ ] Existing code style preserved in all touched files
- [ ] No hardcoded secrets, API keys, or private keys

## API (`apps/api`)

- [ ] If a SQLAlchemy model changed → Alembic migration generated (`apps/api/alembic/versions/`)
- [ ] New models registered in `apps/api/models/__init__.py`
- [ ] New routes registered in `apps/api/routes/__init__.py`
- [ ] DB access goes through a repository, not inline in the route

## Worker (`apps/worker`)

- [ ] New Celery tasks registered/imported so they're picked up by the worker
- [ ] Config values added to `apps/worker/config/settings.py` (`Config` class), not scattered `os.getenv()`
- [ ] Any trade-execution change defaults to Sepolia / DRY_RUN, never mainnet, unless explicitly requested
- [ ] `WALLET_PRIVATE_KEY` / `WEB3_WALLET_PRIVATE_KEY` never logged or printed

## Verification

- [ ] Ask user to verify the bug is fixed / feature is working before committing
- [ ] No destructive Docker command (`down`, image rm, volume prune) run without explicit instruction
