---
description: Update docs/ after a feature or major bug fix
---

# Update Docs Workflow

`docs/` is currently empty — this workflow governs how to start populating it, not how to update
an established set of files.

## 1. Check Existing Docs

1. List `docs/` — as of 2026-07-17 it has no files.
2. If a related doc already exists from prior work, update it; otherwise create a new one.

## 2. New Feature — Create `docs/<FEATURE_NAME>.md`

```markdown
# <Feature Name>

## Overview
What it does (1-2 sentences).

## Implementation Details
- Key technical decisions
- External services used (CoinGecko, DexScreener, LLM provider, Infura, Uniswap)
- Data flow summary

## Files Created/Modified
**API:**
- `apps/api/models/<file>.py`
- `apps/api/routes/<file>.py`

**Worker:**
- `apps/worker/tasks/<file>.py`
- `apps/worker/core/<file>.py`

**Webapp (if applicable):**
- `apps/webapp/src/<file>.tsx`

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/...` | ... |

## Database Changes
New models/tables/migrations if any.
```

## 3. Major Bug Fix — Create `docs/<BUG_NAME>_FIX.md`

```markdown
# <Bug Description> Fix

## Problem Summary
What was broken and how it manifested.

## Root Cause
Technical explanation.

## Solution
What was changed and why.

## Files Modified
- `apps/api/...`
- `apps/worker/...`
```

## 4. README

Once `docs/` has more than a couple of files, add a `docs/README.md` index — don't create one
prematurely for a single doc.

## Checklist

- [ ] Checked `docs/` for existing related docs
- [ ] Created or updated the feature/bug doc
- [ ] Added a `docs/README.md` index entry once there are 3+ docs
