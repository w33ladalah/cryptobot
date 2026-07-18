---
description: Fix a bug in the admin panel (Next.js)
---

# Admin Bug Fixing Workflow

## 1. Understand the Bug

- Identify the bug symptoms and error messages
- Locate the affected code in `admin/src/`
- Check browser console for JavaScript errors
- Check browser network tab for failed API requests

## 2. Reproduce the Bug

- Navigate to the affected page in the admin panel (http://localhost:3001)
- Perform the actions that trigger the bug
- Note the exact steps to reproduce

## 3. Identify Root Cause

- Trace the code flow from component to API service
- Check for:
  - Missing error handling in API service fetch calls
  - Incorrect API endpoint or method
  - Missing or incorrect TypeScript types
  - State management issues (Redux state not updating)
  - Incorrect component lifecycle or useEffect dependencies
  - Missing auth token or incorrect token handling
  - UI state not syncing with API response

## 4. Implement the Fix

- Make minimal changes to fix the root cause
- Follow admin conventions:
  - Use `fetch()` for API calls with Bearer token
  - Define TypeScript interfaces in service files
  - Use Lucide icons (not Phosphor or MUI icons)
  - Use TailwindCSS v4 for styling
  - No redux-persist (state resets on reload)
- Do not refactor unrelated code

## 5. Test the Fix

- Refresh the admin page
- Perform the reproduction steps again
- Verify the bug is fixed
- Check that the fix doesn't break related functionality

## 6. Update Documentation (if major bug)

If this is a major bug fix (affects user-facing behavior, fixes race condition, data integrity issue, etc.):

- Create `docs/fixed-bugs/<BUG_NAME>_FIX.md` with:
  - Problem summary
  - Root cause
  - Solution
  - Files modified
- Update `docs/README.md` to add the new doc

## 7. Commit

- Commit with a descriptive message: `fix(admin): <description>`
- Reference any related issue if applicable

## Important Notes

- Admin uses Next.js 16 (not 15 like frontend)
- Admin uses native `fetch()` (not Axios like frontend)
- Admin hits `/api/admin/*` endpoints on the backend
- Admin has no canvas/Konva editing
- Admin has no redux-persist (no client-side persistence)
