---
description: Update docs/ after a feature or major bug fix
---

# Update Docs Workflow

Use this after completing a new feature or major bug fix to keep `docs/` in sync.

## 1. Check Existing Docs

1. Read `docs/README.md` to understand the current index.
2. Search `docs/` for any existing file related to the feature/bug area.
3. If a related doc exists → **update it**. If not → **create a new one**.

## 2. New Feature — Create `docs/<FEATURE_NAME>.md`

Use this structure:

```markdown
# <Feature Name>

## Overview
What it does (1-2 sentences).

## Implementation Details
- Key technical decisions
- AI models or external services used
- Data flow summary

## Files Created/Modified
**Backend:**
- `backend/app/models/<file>.py`
- `backend/app/routers/<file>.py`

**Frontend:**
- `frontend/src/store/slices/<file>.ts`
- `frontend/src/app/<page>/page.tsx`

**Admin (if applicable):**
- `admin/src/app/<page>/page.tsx`

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/...` | Bearer | ... |

## Database Changes
New models/tables/migrations if any.

## Points Cost
Service alias and point type if the feature consumes points.
```

## 3. Major Bug Fix — Create `docs/<BUG_NAME>_FIX.md`

Use this structure:

```markdown
# <Bug Description> Fix

## Problem Summary
What was broken and how it manifested.

## Root Cause
Technical explanation of why the bug occurred.

## Solution
What was changed and why.

## Files Modified
- `backend/app/...`
- `frontend/src/...`
```

## 4. Update `docs/README.md`

Add the new doc under the correct section:

- **Feature Implementation Docs** — for new features
- **Bug Fix Logs** — for bug fixes
- **Authentication & OAuth** — for auth-related docs

Format: `- [**FILENAME.md**](FILENAME.md) — Short description`

## 5. Update Related Core Docs (if applicable)

- **New API endpoint added** → update `docs/API_REFERENCE.md` with the new endpoint.
- **Major new capability** → update `docs/FEATURES.md` with the feature entry.
- **Architecture change** → update `docs/ARCHITECTURE.md`.

## Checklist

<!-- checklist -->
- [ ] Checked `docs/README.md` for existing related docs
- [ ] Created or updated the feature/bug doc in `docs/`
- [ ] Added entry to `docs/README.md`
- [ ] Updated `docs/API_REFERENCE.md` if new endpoints were added
- [ ] Updated `docs/FEATURES.md` if a major capability was added
