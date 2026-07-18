---
description: Decide whether a feature or bug fix needs unit tests
---

# Should I Write Unit Tests?

Use this after implementing a feature or fixing a bug to decide if unit tests are warranted.

## Decision Flow

### 1. Does the change involve PURE LOGIC or CALCULATIONS?

**Yes — functions with deterministic inputs/outputs that don't touch DB or HTTP** → **Write unit tests**
- Examples: `calculate_license_expiration()`, `is_license_expired()`, date math, point cost calculations, metadata builders, string formatters
- Indicators: Function lives in `core/`, `utils/`, has no `async def`, no DB session, no HTTP call
- Test file: `backend/tests/test_<module_name>.py`

**No** → Continue to Question 2

### 2. Is this a BUG FIX for logic that COULD SILENTLY REGRESS?

**Yes — the bug was non-obvious and the fix is a small targeted change** → **Write a regression test**
- Examples: wrong date calculation, off-by-one in expiration, enum `.value` comparison mistake, base64 decoding edge case
- Indicators: The bug was hard to spot in code review; a test would have caught it immediately
- Write the test BEFORE or alongside the fix — even one test covering the broken case is enough

**No** → Continue to Question 3

### 3. Does the change involve COMPLEX BRANCHING with multiple code paths?

**Yes — 3+ conditional branches, each producing different outcomes** → **Write unit tests**
- Examples: license resolution logic, point deduction rules, download eligibility checks, fallback chains
- Indicators: `if/elif/else` chains, multiple `raise HTTPException(...)` paths, fallback to legacy fields
- Focus on the branches that are hardest to exercise manually in dev

**No** → Continue to Question 4

### 4. Is this an INTEGRATION POINT that's hard to test manually?

**Yes — involves Celery tasks, WebSocket events, background tasks, or async polling** → **Write integration or async unit tests**
- Examples: `validate_and_backfill_license_expiration`, polling loop, WebSocket message handler
- Use `pytest.mark.asyncio`, `AsyncMock`, `MagicMock` — see `backend/tests/test_license_utils.py` for patterns
- Mock external services (DB, S3, Replicate) rather than calling them

**No** → Continue to Question 5

### 5. Is this a SIMPLE WIRING CHANGE?

**Yes — adding a field to a schema, registering a router, updating a config value, CSS tweak** → **Skip tests**
- Examples: adding a column to a Pydantic schema, registering a new endpoint, changing a default value
- These are better verified by running the app and checking the response manually

**No / Not sure** → Apply the **"Would it break silently?" test**: If someone refactors this function in 6 months, would a bug be immediately caught by a test? If yes → write a test. If no → skip.

## Skip Tests If

- CRUD boilerplate (create/get/update/delete with no special logic)
- Schema field addition only
- Router registration or middleware config
- UI/CSS changes
- Migration-only change
- Simple one-line fix to a string or constant value

## Write Tests If

- Pure calculation or transformation function
- Logic that has multiple conditional branches
- Bug fix for a non-obvious regression risk
- Async utility function that is hard to test end-to-end manually
- Validation logic (e.g., expiration checks, ownership checks, status guards)
- Any function that lives in `core/` or `utils/`

## Quick Reference

| Change Type | Write Test? | Test Type |
|-------------|-------------|-----------|
| Pure calculation function | Yes | Unit (sync) |
| Expiration / date logic | Yes | Unit (sync) |
| Multi-branch validation | Yes | Unit (sync) |
| Async utility (DB-touching) | Yes | Unit (async, mock DB) |
| Bug fix (regression risk) | Yes | Regression unit test |
| CRUD boilerplate | No | — |
| Schema field add | No | — |
| Router registration | No | — |
| CSS / UI tweak | No | — |

## Where to Put Tests

- All backend tests: `backend/tests/test_<module_name>.py`
- Existing examples:
  - `backend/tests/test_license_utils.py` — pure function + async utility tests
  - `backend/tests/test_face_swap_workflow.py` — endpoint integration tests with `TestClient`
- Run tests inside Docker:
  ```bash
  docker compose exec backend pytest backend/tests/test_<module_name>.py -v
  ```
- Run all tests:
  ```bash
  docker compose exec backend pytest backend/tests/ -v
  ```

## Checklist

- [ ] Evaluated the change against the decision flow
- [ ] Determined: Write tests / Skip tests
- [ ] If writing: created `backend/tests/test_<module_name>.py` with focused test cases
- [ ] If writing: covered both the happy path AND the key failure/edge cases
- [ ] If writing: verified tests pass inside Docker
