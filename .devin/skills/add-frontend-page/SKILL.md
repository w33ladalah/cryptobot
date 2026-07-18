---
name: add-frontend-page
description: Add a new frontend page with Redux slice, thunk, and component wiring
---

# Add Frontend Page with Redux

Given a **feature name** and **API endpoints**, scaffold the frontend page with full Redux wiring:

## What to generate

### 1. API Endpoints — `frontend/src/constants/apiEndpoints.ts`

Add new entries to the `API_ENDPOINTS` object:

```typescript
<FEATURE>: {
  LIST: `${API_BASE_URL}/api/<feature>`,
  GET: (id: string) => `${API_BASE_URL}/api/<feature>/${id}`,
  CREATE: `${API_BASE_URL}/api/<feature>`,
  UPDATE: (id: string) => `${API_BASE_URL}/api/<feature>/${id}`,
  DELETE: (id: string) => `${API_BASE_URL}/api/<feature>/${id}`,
},
```

### 2. Redux Slice — `frontend/src/store/slices/<feature>Slice.ts`

- Export the state interface: `<Feature>State`.
- Include `items`, `loading`, `error` at minimum.
- Add domain-specific reducers as needed.
- Wire `extraReducers` for the thunks (pending/fulfilled/rejected).

### 3. Redux Thunk — `frontend/src/store/thunks/<feature>Thunks.ts`

- Use `createAsyncThunk` with `AppThunkConfig` typing.
- Import `api` from `@/utils/api` and `API_ENDPOINTS` from `@/constants/apiEndpoints`.
- Create thunks for: fetch list, fetch single, create, update, delete as needed.

### 4. Register in Store — `frontend/src/store/store.ts`

- Import the reducer and state type.
- Add to `RootState` interface.
- Add to `combineReducers` call.
- Add to `clearedState` in `RESET_EXCEPT_AUTH` handler if it should reset on logout.

### 5. Page Component — `frontend/src/app/<feature>/page.tsx`

- `"use client"` directive.
- Use `useAppDispatch()` and `useAppSelector()` from `@/store/hooks`.
- Dispatch thunks in `useEffect`.
- Style with TailwindCSS + MUI components as appropriate.
- Include loading spinners and error handling.

### 6. Types (if needed) — `frontend/src/types/<feature>.ts`

- Define TypeScript interfaces for the API response shapes.
- Import these in the slice/thunk files.

## Conventions

- Always use **typed hooks** (`useAppDispatch`, `useAppSelector`) — never plain `useDispatch`/`useSelector`.
- HTTP via the shared **Axios instance** (`@/utils/api`) — never raw `fetch()`.
- Icons: use **Phosphor Icons** (`@phosphor-icons/react`) or **MUI Icons**.
- Font: Nunito (already configured in Tailwind).
