---
trigger: glob
globs: admin/**
description: Admin panel conventions for Next.js 16, Lucide icons, fetch-based services, TailwindCSS
---

# Admin Panel Conventions

## Tech Stack (Different from Frontend!)

- **Next.js 16** (frontend is 15)
- **Lucide React** icons (frontend uses Phosphor + MUI icons)
- **Native `fetch()`** for API calls (frontend uses Axios)
- **No redux-persist** (state resets on reload)
- **No canvas/Konva** editing
- TailwindCSS v4, TipTap (rich text), @dnd-kit/core (drag & drop)
- Font: Geist + Geist Mono

## Directory Layout

```
admin/src/
├── app/          → CRUD pages (gallery, talents, users, pricing, etc.)
├── components/   → AuthGuard, ReduxProvider, shared UI
└── services/     → One service file per entity
```

## API Services Pattern

```typescript
// admin/src/services/myEntity.ts
export interface MyEntity { id: string; name: string; ... }

export async function fetchMyEntities(token: string): Promise<MyEntity[]> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/my-entities`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}
```

- Base URL from `NEXT_PUBLIC_API_URL`
- Always include `Authorization: Bearer ${token}`
- Always target `/api/admin/*` endpoints

## Layout

- `layout.tsx` is NOT `"use client"` — server-side layout
- Uses `Metadata` export for SEO

## Auth

- `AuthGuard` wraps all routes in `layout.tsx`
- Admin users require `is_admin: true` or `is_superuser: true`

## Key Differences from Frontend

| Aspect | Frontend | Admin |
|--------|----------|-------|
| Next.js version | 15 | 16 |
| Icons | Phosphor + MUI | Lucide |
| HTTP client | Axios | Native fetch |
| State persistence | redux-persist | No persistence |
| Canvas | Konva | None |
| API base | `NEXT_PUBLIC_API_BASE_URL` | `NEXT_PUBLIC_API_URL` |
