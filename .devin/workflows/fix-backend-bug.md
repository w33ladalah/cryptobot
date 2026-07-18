---
description: Fix a bug in the api or worker service
---

# API / Worker Bug Fixing Workflow

## 1. Understand the Bug

- Identify the symptoms and any error message/traceback.
- Locate the affected code: `apps/api/` (routes/repositories/models) or `apps/worker/`
  (tasks/core/llm) — confirm which service before assuming.
- Check container logs:
  ```bash
  docker compose -f docker/run-development-compose.yaml logs api --tail 100
  docker compose -f docker/run-development-compose.yaml logs worker --tail 100
  ```

## 2. Reproduce the Bug

- API: hit the endpoint via `http://localhost:<API_PORT>/docs` (Swagger) or curl.
- Worker: check if it's a scheduled/beat task (`apps/worker/bot.py`) or triggered by an API call;
  reproduce by triggering the task and reading worker logs.
- If the bug is in `apps/worker/core/trading/`, check `rules/worker/known-bugs.md` first — it may
  already be a documented, confirmed bug rather than something new.

## 3. Identify Root Cause

- Trace the code flow from entry point (route or task) to the error.
- Check for: missing error handling, incorrect repository queries, config values referenced but
  not defined on `Config` (a recurring issue in this codebase — see known-bugs.md), signature
  mismatches between a function and its call site, or SecretStr values used where a plain string
  is expected.

## 4. Implement the Fix

- Make minimal changes to fix the root cause, not a downstream symptom.
- Follow `rules/backend/conventions.md` for API/worker patterns.
- Do not refactor unrelated code.

## 5. Test the Fix

- API: exercise the endpoint via Swagger/curl.
- Worker: trigger the task and confirm via logs / DB state.
- If the fix touches trade execution, confirm it still defaults to Sepolia/DRY_RUN — see
  `rules/always-on/safety.md`.

## 6. Commit

- Commit with a descriptive message: `fix(api): <description>` or `fix(worker): <description>`.

## Important Notes

- `api` hot-reloads (`fastapi dev`) — never restart it for a plain code change.
- `worker` does **not** hot-reload — a restart is usually needed after editing `apps/worker/**`.
  See `adr/004-no-backend-container-restart.md`.
- If the fix requires a schema change, use `/database-migration`.
