---
description: Fix a backend bug in FastAPI application
---

# Backend Bug Fixing Workflow

## 1. Understand the Bug

- Identify the bug symptoms and error messages
- Locate the affected code in `backend/app/`
- Check logs from Docker container: `docker compose logs backend --tail 100`
- Check Sentry for error details if applicable

## 2. Reproduce the Bug

- Write a test case or manual reproduction steps
- If using Swagger UI at http://localhost:8000/docs, test the endpoint
- If the bug is in a Celery task, check worker logs: `docker compose logs celery-worker --tail 100`

## 3. Identify Root Cause

- Trace the code flow from entry point (router) to the error
- Check for:
  - Missing error handling (try/except blocks)
  - Incorrect database queries or session usage
  - Missing or incorrect dependencies
  - Incorrect environment variable usage
  - Race conditions in async code
  - Missing or incorrect auth dependencies

## 4. Implement the Fix

- Make minimal changes to fix the root cause
- Follow backend conventions:
  - Use async/await properly with SQLAlchemy 2.0
  - Use `get_db` dependency for database sessions
  - Use proper auth dependencies (`get_current_active_user`, etc.)
  - Return proper HTTP status codes with `HTTPException`
- Do not refactor unrelated code

## 5. Test the Fix

- Run the affected endpoint via Swagger UI or curl
- If the fix involves a database change, ensure it doesn't break existing data
- Check that the fix doesn't introduce new issues

## 6. Update Documentation (if major bug)

If this is a major bug fix (affects user-facing behavior, fixes race condition, data integrity issue, etc.):

- Create `docs/<BUG_NAME>_FIX.md` with:
  - Problem summary
  - Root cause
  - Solution
  - Files modified
- Update `docs/README.md` to add the new doc

## 7. Commit

- Commit with a descriptive message: `fix(backend): <description>`
- Reference any related issue if applicable

## Important Notes

- Never restart the backend container — uvicorn `--reload` will pick up changes
- Always run backend commands inside Docker: `docker compose exec backend <command>`
- If the fix requires a database migration, use `/database-migration` workflow
