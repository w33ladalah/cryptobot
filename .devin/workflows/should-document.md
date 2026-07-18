---
description: Decide if the current conversation warrants documentation in docs/
---

# Should I Document This?

Use this at the end of a conversation (or after a significant change) to decide whether formal documentation in `docs/` is needed.

## Decision Flow

### 1. Did you add a NEW feature or capability?

**Yes — new endpoint, new page, new service, new model** → **Document it**
- Create `docs/<FEATURE_NAME>.md` using the `/update-docs` workflow
- Examples: new video download system, new quick tool, new admin CRUD page
- Indicators: new router file, new migration, new frontend page

**No** → Continue to Question 2

### 2. Did you fix a MAJOR bug?

**Yes — changed behavior, fixed data integrity, fixed race condition, fixed user-facing issue** → **Document it**
- Create `docs/<BUG_NAME>_FIX.md` using the `/update-docs` workflow
- Examples: download counting wrong, points not deducted, auth modal showing incorrectly
- Indicators: multiple files changed, root cause was non-obvious, could regress

**No, it was minor** → Continue to Question 3

### 3. Did you change existing architecture or data flow?

**Yes — changed how systems connect, modified database schema, altered auth flow** → **Update existing docs**
- Update `docs/ARCHITECTURE.md`, `docs/FEATURES.md`, or the relevant feature doc
- Examples: changed download history to a single table, added new WebSocket channel, changed points deduction flow

**No** → Continue to Question 4

### 4. Did you add new API endpoints?

**Yes** → **Update `docs/API_REFERENCE.md`** (even if no standalone doc is needed)

**No** → Continue to Question 5

### 5. Was this a trivial change?

**Yes — typo fix, CSS tweak, one-line config change, dependency bump** → **Skip documentation**

**Not sure** → Apply the **"Would a new developer be confused?" test**: If someone new joined tomorrow and saw this change in git log, would they need context to understand why it was made? If yes → document it. If no → skip.

## Skip Documentation If

- Single-line cosmetic fix (CSS, typo, whitespace)
- Dependency version bump with no behavior change
- Config/env var change only
- Refactoring with no behavior change (and no new patterns)
- Adding comments or inline docs only
- Temporary debugging code that was removed

## Document If

- New feature (any size)
- Bug fix that changes user-facing behavior
- Bug fix with non-obvious root cause that could regress
- Schema/migration changes
- New API endpoints
- New external service integration
- Changed data flow between existing systems
- New conventions or patterns introduced

## Quick Reference

| Change Type | Document? | Where |
|-------------|-----------|-------|
| New feature | Yes | `docs/<FEATURE>.md` + README + API_REFERENCE + FEATURES |
| Major bug fix | Yes | `docs/<BUG>_FIX.md` + README |
| New API endpoint | Yes | `docs/API_REFERENCE.md` |
| Architecture change | Yes | Update existing doc |
| Minor bug fix (1-2 lines) | No | — |
| CSS/styling tweak | No | — |
| Config change only | No | — |
| Refactor (no behavior change) | No | — |

## After Deciding "Yes"

Run the `/update-docs` workflow to create or update the appropriate documentation.

## Checklist

- [ ] Evaluated the conversation against the decision flow
- [ ] Determined: Document / Update existing / Skip
- [ ] If documenting: ran `/update-docs` workflow
- [ ] If skipping: confirmed the change is truly trivial
