---
description: Decide whether a feature or bug fix needs unit tests
---

# Should I Write Unit Tests?

Use this after implementing a feature or fixing a bug to decide if unit tests are warranted.

## Decision Flow

### 1. Does the change involve PURE LOGIC or CALCULATIONS?

**Yes — deterministic inputs/outputs, no DB/HTTP** → **Write unit tests**
- Examples: position-size calculation, slippage math, LLM decision parsing, date/interval math
- Indicators: function lives in `core/`, `utils/`, no DB session, no HTTP call
- Test file: `apps/worker/tests/test_<module_name>.py` (existing tests live here)

**No** → Continue to Question 2

### 2. Is this a BUG FIX for logic that COULD SILENTLY REGRESS?

**Yes — non-obvious bug, small targeted fix** → **Write a regression test**
- Examples: the config-attribute bugs and signature mismatch in
  `rules/worker/known-bugs.md` are exactly this category — once fixed, a regression test
  should assert the previously-broken behavior now works.

**No** → Continue to Question 3

### 3. Does the change involve COMPLEX BRANCHING with multiple code paths?

**Yes — 3+ conditional branches with different outcomes** → **Write unit tests**
- Examples: BUY/SELL/HOLD decision routing, fallback chains across LLM adapters or data sources

**No** → Continue to Question 4

### 4. Is this a TRADE-EXECUTION or MONEY-MOVING path?

**Yes** → **Always write tests**, and always exercise them against Sepolia/DRY_RUN before
considering the change done — this is the one category in this project where "skip tests" is
never the right answer, regardless of how small the change looks.

**No** → Continue to Question 5

### 5. Is this a SIMPLE WIRING CHANGE?

**Yes — adding a field to a schema, registering a router, config default, CSS tweak** →
**Skip tests**, verify manually instead.

## Where to Put Tests

- Worker tests: `apps/worker/tests/test_<module_name>.py`
- API repository tests: `apps/api/repositories/tests/`
- Run inside Docker:
  ```bash
  docker compose -f docker/run-development-compose.yaml exec worker pytest apps/worker/tests/ -v
  docker compose -f docker/run-development-compose.yaml exec api pytest apps/api/repositories/tests/ -v
  ```

## Checklist

- [ ] Evaluated the change against the decision flow
- [ ] If it's a trade-execution path — tests written, no exceptions
- [ ] If writing: covered both the happy path AND key failure/edge cases
- [ ] Verified tests pass inside Docker
