---
description: End-to-end workflow for adding a new feature
---

# Add New Feature Workflow

Use this when adding a feature that may touch the API, worker, and/or webapp. Scope down to only
the services actually needed — most changes here are single-service.

## Phase 1 — API (`apps/api`), if needed

1. **Model:** create/update in `apps/api/models/`, register in `apps/api/models/__init__.py`.
2. **Migration:** generate + apply Alembic migration (`/database-migration`).
3. **Schema:** add to `apps/api/schema/`.
4. **Repository:** add to `apps/api/repositories/`.
5. **Route:** add to `apps/api/routes/`, register in `apps/api/routes/__init__.py`
   (`/add-api-endpoint`).

## Phase 2 — Worker (`apps/worker`), if needed

6. **Config:** add any new env-driven values to `apps/worker/config/settings.py`'s `Config` class.
7. **Task:** add to `apps/worker/tasks/`, wire into `apps/worker/bot.py` / `main.py` (Celery app,
   beat schedule if recurring).
8. **LLM adapter (if a new LLM provider):** add under `apps/worker/llm/adapters/` following the
   existing adapter interface — don't call an LLM SDK directly from a task.
9. **Trade execution (if touching chain logic):** stays inside `apps/worker/core/trading/` —
   check `rules/worker/known-bugs.md` first, this area has several open bugs.

## Phase 3 — Webapp (`apps/webapp`), if needed

10. `apps/webapp` currently has no API client, routing, or state library wired up — if the
    feature needs a UI, propose an approach first rather than assuming an established pattern
    (see `rules/frontend/conventions.md`).

## Phase 4 — Verification

- [ ] Migration applied and verified (`alembic current`) if models changed
- [ ] Endpoint tested via Swagger/curl if API changed
- [ ] Task triggered and logs checked if worker changed
- [ ] Trade-execution changes verified against Sepolia/DRY_RUN, not mainnet
- [ ] Tested end-to-end where applicable
