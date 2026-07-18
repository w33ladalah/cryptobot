---
trigger: glob
globs: frontend/**
description: Frontend conventions for Next.js 15, React 19, Redux Toolkit, Axios, TailwindCSS v4, MUI 7
---

# Frontend Conventions

## Tech Stack

- Next.js 15 (App Router, typed routes)
- React 19.2
- Redux Toolkit + redux-persist
- TailwindCSS v4 + MUI 7 + Phosphor Icons + react-icons
- Axios with interceptors (`src/utils/api.ts`)
- Konva + react-konva (canvas editing — custom webpack config)
- Font: Nunito

## Directory Layout

```
frontend/src/
├── app/             → Next.js App Router pages
├── components/      → Shared components (flat structure)
├── constants/       → API_ENDPOINTS (apiEndpoints.ts)
├── hooks/           → Custom hooks
├── providers/       → Context providers (Redux, Error, MUI)
├── services/        → WebSocket service modules
├── store/
│   ├── slices/      → One Redux slice per domain
│   ├── thunks/      → One thunk file per domain
│   ├── hooks.ts     → useAppDispatch / useAppSelector
│   └── store.ts     → Store config, RootState, persistor
├── types/           → TypeScript type definitions
└── utils/           → api.ts, errorHandler.ts, image utils
```

## Redux Rules

- **Always** use typed hooks: `useAppDispatch()` and `useAppSelector()` from `store/hooks.ts`
- One slice + one thunk file per domain
- Thunks use `createAsyncThunk` with `AppThunkConfig`
- **Persisted slices**: `generator`, `auth`, `ui` only — others reset on reload
- Handle `RESET_STATE` and `RESET_EXCEPT_AUTH` in slice `extraReducers` if needed

## API Layer

- **All API calls** via Axios instance: `import api from '@/utils/api'`
- **All endpoints** defined in `src/constants/apiEndpoints.ts` — never inline URL strings
- 10-minute timeout on AI operations
- Auto token refresh on 401 responses

## Styling

- TailwindCSS v4 as primary approach
- MUI 7 for complex components (modals, sliders, tabs)
- Phosphor Icons (NOT Lucide — that's admin)
- Font: Nunito (`font-sans`)

## Auth Modal Behavior

Auth modal only shows to users with existing `localStorage.refreshToken` (expired session). Fresh unauthenticated visitors get NO auth modal — 401s are silently swallowed.

## Header Badge (Generation Success)

- Photo-model image: dispatched via `setActiveGenerationCounts` from `ImageGrid.tsx`
- Non-image (video, talking video): dispatch `setTalkingVideoSucceeded(1)` on success

```typescript
import { setTalkingVideoSucceeded } from '@/store/slices/generatorSlice';
dispatch(setTalkingVideoSucceeded(1));
```

## Video Download Blobs

```typescript
const res = await api.post(url, data, { responseType: 'blob' });
// Error handling — must parse blob as text then JSON:
if (error.response?.data instanceof Blob) {
  const text = await error.response.data.text();
  const errorData = JSON.parse(text);
}
```

## Images

- `unoptimized: true` in Next.js config (imgproxy handles optimization)
- Remote patterns configured for S3, CloudFront, imgproxy

## Dev Server

```bash
npm run dev          # port 3000
npm run dev:turbo    # Turbopack
```

`next.config.ts` rewrites `/api/*` → `http://127.0.0.1:8000/api/*` for local dev.
