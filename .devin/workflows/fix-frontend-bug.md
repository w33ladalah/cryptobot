---
description: Fix a bug in the frontend (Next.js)
---

# Frontend Bug Fixing Workflow

## 1. Understand the Bug

- Identify the bug symptoms and error messages
- Locate the affected code in `frontend/src/`
- Check browser console for JavaScript errors
- Check browser network tab for failed API requests
- Check Redux DevTools for state issues

## 2. Reproduce the Bug

- Navigate to the affected page in the frontend (http://localhost:3000)
- Perform the actions that trigger the bug
- Note the exact steps to reproduce

## 3. Identify Root Cause

- Trace the code flow from component to thunk to API
- Check for:
  - Missing error handling in thunks (rejectWithValue)
  - Incorrect API endpoint in `apiEndpoints.ts`
  - Missing or incorrect TypeScript types
  - Redux state not updating properly (extraReducers)
  - Incorrect component lifecycle or useEffect dependencies
  - Missing auth token or incorrect token handling
  - WebSocket connection issues (for real-time features)
  - Konva canvas state issues (for image editing)

## 4. Implement the Fix

- Make minimal changes to fix the root cause
- Follow frontend conventions:
  - Use Axios from `src/utils/api.ts` for API calls
  - Use typed hooks: `useAppDispatch()` and `useAppSelector()`
  - Thunks use `createAsyncThunk` with `AppThunkConfig`
  - Redux slices have corresponding thunk files
  - Use TailwindCSS v4 and MUI 7 for styling
  - Use Phosphor Icons (not Lucide)
- Do not refactor unrelated code

## 5. Test the Fix

- Refresh the frontend page
- Perform the reproduction steps again
- Verify the bug is fixed
- Check that the fix doesn't break related functionality
- If the bug involves persisted state, test after page reload

## 6. Update Documentation (if major bug)

If this is a major bug fix (affects user-facing behavior, fixes race condition, data integrity issue, etc.):

- Create `docs/<BUG_NAME>_FIX.md` with:
  - Problem summary
  - Root cause
  - Solution
  - Files modified
- Update `docs/README.md` to add the new doc

## 7. Commit

- Commit with a descriptive message: `fix(frontend): <description>`
- Reference any related issue if applicable

## Important Notes

- Frontend uses Next.js 15 (not 16 like admin)
- Frontend uses Axios (not native fetch like admin)
- Frontend uses Redux Toolkit with redux-persist (unlike admin)
- Frontend uses Phosphor Icons (not Lucide like admin)
- Frontend has Konva canvas for image editing (admin does not)
- Frontend API calls are proxied via Next.js rewrites in `next.config.ts`
